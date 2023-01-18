from shapely.geometry import Point, Polygon
import geopandas as gpd
import pandas as pd
import folium
import uuid
from datetime import date
import json
import openrouteservice
import os
from dotenv import load_dotenv
load_dotenv('.env')


def csv_to_gdf(filepath):
    df = pd.read_csv(filepath, nrows=0)

    if not set(['id','latitude','longitude']).issubset(df.columns):
        s = ','.join(map(str, list(df.columns)))
        raise ValueError(f'Wrong column names, columns should be called id, latitude, longitude, received {s}')

    df = pd.read_csv(filepath)

    df['uuid'] = df.apply(lambda x: uuid.uuid4(), axis=1)
    
    geometry = [Point(lon,lat) for lon, lat in zip(df['longitude'], df['latitude'] )]

    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

    return gdf


def fetch_drivetime(poi, time_range):
    # authentication OpenRouteService
    secret = os.getenv("ORS_SECRET")
    ors = openrouteservice.Client(key=secret)

    isochrone = ors.isochrones(locations=[[poi['longitude'], poi['latitude']]], range=[time_range])

    isochrone['features'][0]['properties']['id'] = poi['id']

    with open(f"./geojson/{poi['id']}_{date.today()}.geojson", 'w') as output_file:
        json.dump(isochrone, output_file, ensure_ascii=False, indent=4)

    

#######    

gdf = csv_to_gdf("./dummy/p.csv")

# print(gdf.head())

# poi = {
#     'longitude': 4.4158472,
#     'latitude': 51.2452363,
#     'id': 'Antwerp-Kinepolis'
# }

# fetch_drivetime(poi, 900)