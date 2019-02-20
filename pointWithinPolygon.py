import ogr, gdal
import pandas as pd
import json
from shapely.geometry import Polygon, Point, MultiPolygon
import shapefile


def shape_crop(feat, lyr):

    raster = gdal.Open('NaturalColorwithDRA.tiff')
    # vector = ogr.Open('geoch_centroid.shp')

    # Get raster geometry
    transform = raster.GetGeoTransform()
    pixelWidth = transform[1]
    pixelHeight = transform[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize

    xLeft = transform[0]
    yTop = transform[3]
    xRight = xLeft+(cols*pixelWidth)
    yBottom = yTop+(rows*pixelHeight) #pixcelheight is a negative value

    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(xLeft, yTop)
    ring.AddPoint(xLeft, yBottom)
    ring.AddPoint(xRight, yBottom)
    ring.AddPoint(xRight, yTop)
    ring.AddPoint(xLeft, yTop)
    rasterGeometry = ogr.Geometry(ogr.wkbPolygon)
    rasterGeometry.AddGeometry(ring)
    geom = feat.GetGeometryRef()

    # print rasterGeometry
    # print geom
    return rasterGeometry.Contains(geom)

def create_polygon(coords):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for coord in coords:
        for coord1 in coord:
            # print type(coord1)
            # print float(coord1[0]), float(coord1[1])
            ring.AddPoint(float(coord1[0]), float(coord1[1]))  # Adding points for each polygon

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return poly

def poly_contain():
    # Do the json reading
    data = pd.read_json("dlfile.json", orient='records', lines=True)
    df2 = []
    for i in data['features']:
        for j in i:
            df1 = []
            for k in j.values():
                for l in k.values():
                    df1.append(l)
            df2.append(df1)
    df3 = pd.DataFrame(df2)
    # df3.to_csv('testcsv.csv')
    polylist = list()
    for i in df3[0]:
        #print i
        polycoords = i
        poly = create_polygon(polycoords)
        polylist.append(poly)
    return polylist
    #     point = ogr.Geometry(ogr.wkbPoint)
    #     point.AddPoint(feat[0],feat[1])
    #     point.ExportToWkb()
    #     # geom = point.GetGeometryRef()
    #     if poly.Contains(point):
    #         return True
    # return False


# https://gis.stackexchange.com/questions/208546/check-if-a-point-falls-within-a-multipolygon-with-python?rq=1
# path = 'area.shp'
#
# polygon = shapefile.Reader(path)
#
# polygon = polygon.shapes()
#
# shpfilePoints = [ shape.points for shape in polygon ]
#
# print shpfilePoints
#
# polygons = shpfilePoints
#
# for polygon in polygons:
#     poly = Polygon(polygon)
#     print poly