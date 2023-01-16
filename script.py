from shapely.geometry import Point, Polygon
import geopandas as gpd
import pandas as pd
import folium
import uuid

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

    

gdf = csv_to_gdf("./dummy/p.csv")

print(gdf.head())