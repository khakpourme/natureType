import geopandas as gpd
# from shapely import Polygon

def main(filepath):
    # GeoDataFrame creation
    poly = gpd.read_file(filepath)
    poly.head()

    # copy poly to new GeoDataFrame
    points = poly.copy()
    # change the geometry
    points.geometry = points['geometry'].centroid

    # same crs
    points.crs =poly.crs
    points.head()

    # save the shapefile
    points.to_file('area_centroid.shp')
    print "Centroid Shapefile saved."
    centroidshapefilepath = 'area_centroid.shp'
    return centroidshapefilepath

# if __name__ == '__main__':
#     main('area.shp')