import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.cluster import SpectralClustering
import pandas as pd

# Load county shapefile
counties_gdf = gpd.read_file("C:/Users/gurra/Downloads/IL_BNDY_County/IL_BNDY_County_Py.shp")
# Load population data (assuming the first column is "Label")

population_df = pd.read_excel("C:/Users/gurra/Downloads/DECENNIALPL2020.P1-2023-12-25T043449.xlsx", sheet_name="Data")
# Clean county names by removing "County, Illinois" suffix and converting to lowercase
population_df["County"] = population_df["Label"].str.replace(" County, Illinois", "").str.upper()
county_names = population_df.columns[1:].str.replace(" County, Illinois", "").str.upper()
population_data = dict(zip(county_names, population_df.iloc[0, 1:]))
#print(population_df.iloc[-2, 1:])
#print(population_data)

#merged_gdf["population"] = merged_gdf["COUNTY_NAM"].map(population_data)
merged_gdf=counties_gdf.copy()
merged_gdf["population"] = merged_gdf["COUNTY_NAM"].map(population_data)
#merged_gdf["population"] = pd.to_numeric(merged_gdf["population"], errors="coerce")
#merged_gdf["population"].fillna(0, inplace=True)

# Calculate total population and target population per region
merged_gdf["population"] = merged_gdf["population"].str.replace(",", "")
#rows_with_nan = merged_gdf[merged_gdf.isna().any(axis=1)]
#print(rows_with_nan)
merged_gdf["population"] = merged_gdf["population"].apply(int)
total_population = merged_gdf["population"].sum()
target_population = total_population // 4
# Create a graph where nodes represent counties and edges connect intersecting/touching counties
G = nx.Graph()
for idx, row in merged_gdf.iterrows():
    G.add_node(idx, population=row["population"])
    poly1 = row["geometry"]
    for idx2, row2 in merged_gdf.iterrows():
        if idx != idx2:
            poly2 = row2["geometry"]
            if poly1.intersects(poly2) or poly1.touches(poly2):
                G.add_edge(idx, idx2)
# Apply Spectral Clustering
sc = SpectralClustering(n_clusters=4, affinity="precomputed", random_state=42)
labels = sc.fit_predict(nx.adjacency_matrix(G))
merged_gdf["region"] = labels + 1  # Add 1 to make region labels start from 1

# Initialize variables
current_region = 1
current_population = 0
# Iterate through counties and assign regions
for idx, row in merged_gdf.iterrows():
    county_population = row["population"]
    if current_population + county_population <= target_population:
        # Assign the current county to the current region
        merged_gdf.at[idx, "region"] = current_region
        current_population += county_population
    else:
        # Move to the next region
        current_region += 1
        current_population = county_population
        merged_gdf.at[idx, "region"] = current_region
# Adjust population within each region
'''region_populations = merged_gdf.groupby("region")["population"].sum()
print(region_populations)
for region in range(1, 5):
    merged_gdf.loc[merged_gdf["region"] == region, "population"] = target_population
region_populations[region]
print(merged_gdf)
'''

# Plot the equal-population regions
fig, ax = plt.subplots(figsize=(10, 10))
merged_gdf.plot(column="region", cmap="Set3", legend=False, ax=ax, edgecolor="white")
#merged_gdf.plot(column="region", cmap="Set3", legend=False, ax=ax)
#region_populations.plot(column="region", cmap="Set3", legend=False, ax=ax)

plt.title("Equal-Population Contiguous Regions in Illinois")
plt.xlabel("County Names")
ax.set_axis_off()
plt.show()