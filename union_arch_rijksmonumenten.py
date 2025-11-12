# Libraries need to run the script  

import geopandas as gpd
import requests
from pathlib import Path
import fiona
import pandas as pd



# Loading archaeological monitor data
url_arch_mon = "https://data.geo.cultureelerfgoed.nl/openbaar/wfs?request=GetFeature&service=WFS&version=1.1.0&outputFormat=json&typeName=rijksmonumentcontouren"
monitor = gpd.read_file(url_arch_mon)

# Panda settings for showing data (this is foremost done to more easily explore the data while processing it)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

url_landuse = "C://repos//Union_monitor//MONITOR_jan_2025.gpkg" #change path to location of geopackage file

land_use_gpkg = gpd.read_file(url_landuse)

layers = fiona.listlayers(url_landuse)
print("Available layers:")
for layer in layers:
    print("-", layer)

layer_name = "monitor_terrein_landgebruik_vlak" #In Top10vector the layer is called "top10_terrein_vlak"

land_use_layer = gpd.read_file(url_landuse, layer=layer_name)

# Perform union
union_gdf = gpd.overlay(monitor, land_use_layer, how="union") 

# Calculate area for all polygons
union_gdf["area_m2"] = union_gdf.geometry.area

# Define columns that are needed in output csv
columns = ["rijksmonument_nummer", "typelandgebruik", "area_m2"]

# define a new dataframe with selected columns
rm_landuse = union_gdf[columns].copy()

# Perform groupby to sum areas per landuse type
rm_sum_landuse = rm_landuse.groupby(["rijksmonument_nummer", "typelandgebruik"], as_index=False)["area_m2"].sum()

# Parse rijksmonument_nummer to integer (it was a float since the union created NA & nan)
rm_sum_landuse["rijksmonument_nummer"] = rm_sum_landuse["rijksmonument_nummer"].astype(int)



# round the area to 2 decimal places
rm_sum_landuse["area_m2"] = rm_sum_landuse["area_m2"].round(2)

# Save dataframe as csv
rm_sum_landuse.to_csv("landuse_rijksmonument.csv", sep= ";", index=False )