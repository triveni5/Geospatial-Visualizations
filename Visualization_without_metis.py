import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.cluster import SpectralClustering
from shapely.geometry import Polygon
import pandas as pd

# Load Illinois counties shapefile
#counties_gdf = gpd.read_file("C:/Users/gurra/Downloads/united_states_illinois_administrative_boundaries_level6_counties_polygon.zip/united_states_illinois_administrative_boundaries_level6_counties_polygon/united_states_illinois_administrative_boundaries_level6_counties_polygon.shp")
counties_gdf = gpd.read_file("C:/Users/gurra/Downloads/IL_BNDY_County/IL_BNDY_County_Py.shp")
print(counties_gdf.head())
print(counties_gdf.info())
# Convert population column to numeric (coerce non-numeric values to NaN)
population_df = pd.read_excel("C:/Users/gurra/Downloads/DECENNIALPL2020.P1-2023-12-25T043449.xlsx", sheet_name="Data")
# Extract county names and population columns
county_names = population_df.columns[1:]  # Assuming the first column is "Label"
#population_values = population_df.iloc[0, 1:].str.replace(",", "").astype(int)

# Create a dictionary with county names as keys and population as values
#population_data = dict(zip(county_names, population_values))
population_data = dict(zip(county_names, population_df.iloc[-1, 1:]))
# Merge shapefile and population data based on county names
#merged_gdf = counties_gdf.merge(population_df, left_on="county_name", right_on="county_name", how="left")
merged_gdf = counties_gdf.copy()
merged_gdf["population"] = merged_gdf["COUNTY_NAM"].map(population_data)
# Convert population column to numeric (handle any non-numeric values)
merged_gdf["population"] = pd.to_numeric(merged_gdf["population"], errors="coerce")
merged_gdf["population"].fillna(0, inplace=True)

# Calculate total population and target population for equal division
total_population = merged_gdf["population"].sum()
target_population = total_population // 4

# Create a graph for spatial analysis
G = nx.Graph()
for idx, row in merged_gdf.iterrows():
    G.add_node(idx, population=row["population"])

for idx1, row1 in merged_gdf.iterrows():
    poly1 = row1["geometry"]
    for idx2, row2 in merged_gdf.iterrows():
        if idx1 != idx2:
            poly2 = row2["geometry"]
            if poly1.intersects(poly2) or poly1.touches(poly2):
                G.add_edge(idx1, idx2)

# Apply spectral clustering to divide counties into 4 regions
sc = SpectralClustering(n_clusters=4, affinity="precomputed", random_state=42)
labels = sc.fit_predict(nx.adjacency_matrix(G))
# Add region labels to the data frame
merged_gdf["region"] = labels + 1  # Add 1 to make region labels start from 1

# Calculate region populations
region_populations = merged_gdf.groupby("region")["population"].sum()

# Adjust region populations to match the target
for region in range(1, 5):
    merged_gdf.loc[merged_gdf["region"] == region, "population"] *= target_population / region_populations[region]

# Plot the map
fig, ax = plt.subplots(figsize=(10, 10))
merged_gdf.plot(column="region", cmap="Set3", legend=False, ax=ax)
plt.title("Equal-Population Contiguous Regions in Illinois")
plt.xlabel("County Names")
ax.set_axis_off()
plt.show()