import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd



# Load Illinois counties shapefile
counties_gdf = gpd.read_file("C:/Users/gurra/Downloads/united_states_illinois_administrative_boundaries_level6_counties_polygon.zip/united_states_illinois_administrative_boundaries_level6_counties_polygon/united_states_illinois_administrative_boundaries_level6_counties_polygon.shp")
print(counties_gdf.head())
print(counties_gdf.info())
print(counties_gdf["name"])
cook_county_present = "Cook County" in counties_gdf["name"].values
print(f"Cook County present: {cook_county_present}")
counties_gdf["population"] = pd.to_numeric(counties_gdf["population"], errors="coerce")  # Coerce non-numeric values to NaN

# Fill missing population values with 0
counties_gdf["population"].fillna(0, inplace=True)
total_population = counties_gdf["population"].sum()
target_population = total_population // 4
# Assign counties to regions

cumulative_population = 0
region = 1
for idx, row in counties_gdf.iterrows():
    cumulative_population += row["population"]
    if cumulative_population > target_population:
        region += 1
        cumulative_population = 0
    counties_gdf.at[idx, "region"] = region

# Plot the map
counties_gdf.plot(column="region", cmap="Set3", legend=True)
plt.title("Equal-Population Regions in Illinois")
plt.xlabel("County Names")
plt.show()