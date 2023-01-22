from shapely.geometry import Point, Polygon
import geopandas as gpd
import pandas as pd
import folium
import uuid
from datetime import date
import json
import openrouteservice
import geojson
import os
from dotenv import load_dotenv
load_dotenv('.env')


def csv_to_gdf(filepath):
    df = pd.read_csv(filepath, nrows=0)

    if not set(['id', 'latitude', 'longitude']).issubset(df.columns):
        s = ','.join(map(str, list(df.columns)))
        raise ValueError(
            f'Wrong column names, columns should be called id, latitude, longitude, received {s}')

    df = pd.read_csv(filepath)

    if not 'uuid' in df.columns:
        df['uuid'] = df.apply(lambda x: uuid.uuid4(), axis=1)

    geometry = [Point(lon, lat)
                for lon, lat in zip(df['longitude'], df['latitude'])]

    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

    return gdf


def fetch_drivetime(poi, time_range):
    # authentication OpenRouteService
    secret = os.getenv("ORS_SECRET")
    ors = openrouteservice.Client(key=secret)

    isochrone = ors.isochrones(
        locations=[[poi['longitude'], poi['latitude']]], range=[time_range])

    properties = isochrone['features'][0]['properties']
    properties['id'] = poi['id']

    with open(f"./geojson/{poi['id']}_{date.today()}.geojson", 'w') as output_file:
        json.dump(isochrone, output_file, ensure_ascii=False, indent=4)


def geojson_to_gdf():

    file_path = "./geojson/"

    file_list = os.listdir(file_path)

    file_list = [file_path + f for f in file_list]

    gdf = pd.concat([gpd.read_file(file, crs='ESPG:4326')
                    for file in file_list]).set_index('id')

    return gdf

# "epsg:31370"


def fetch_points_in_drivetime(drivetime, points):

    gdf = points.loc[(points['geometry'].within(drivetime) | points['geometry'].touches(drivetime)), 
    ['longitude', 'latitude', 'uuid', 'geometry']]

    return gdf

def create_buffer_gsr(points, range_in_meters, crs):

    # dataframes are passed by reference thus a copy must be created to avoid modifying the original dataframe
    points = points.copy()

    points.crs = crs

    buffer = points.geometry.buffer(range_in_meters)

    buffer_union = buffer.geometry.unary_union

    buffer = gpd.GeoSeries(buffer_union, crs=crs)

    buffer = buffer.explode()

    return buffer

#######

gdf = csv_to_gdf("./dummy/p.csv")

create_buffer_gsr(gdf,300,'epsg:31370')

with open('./dummy/test_geo.geojson', 'r') as f:
    gj = geojson.load(f)

dt = Polygon(gj['features'][0]['geometry']['coordinates'][0])

# fetch_points_in_drivetime(dt, gdf)


# print(gdf.head())

# poi = {
#     'longitude': 4.4158472,
#     'latitude': 51.2452363,
#     'id': 'Antwerp-Kinepolis'
# }

# fetch_drivetime(poi, 900)

# test = geojson_to_gdf()

# print(test.head())
