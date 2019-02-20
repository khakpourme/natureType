import ogr, osr
import pandas as pd
import json
# https://gis.stackexchange.com/questions/246655/how-to-create-line-polygon-shapefiles-from-geojson-using-gdal-in-python
# Function to create polygon from geometries
def create_polygon(coords):
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for coord in coords:
        for coord1 in coord:
            # print type(coord1)
            # print float(coord1[0]), float(coord1[1])
            ring.AddPoint(float(coord1[0]), float(coord1[1])) # Adding points for each polygon

    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return poly.ExportToWkt()

def create_point_shape(pointdf):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    pointshapefilepath = "/Data/point.shp"
    point_data_source = driver.CreateDataSource(pointshapefilepath)

    # srs = osr.SpatialReference()
    # srs.ImportFromEPSG(32633)

    # Point shapefile setup
    p_layer = point_data_source.CreateLayer("point_layer", None, ogr.wkbPoint)
    field_testfield = ogr.FieldDefn("fld_a", ogr.OFTString)
    field_testfield.SetWidth(50)
    p_layer.CreateField(field_testfield)

    # Do the point reading
    count = 0
    for i in pointdf['Point']:
        # geo = i.get('geometry')
        # geo_type = geo.get('type')
        # if geo_type == 'Point':  # If it's a point feature, do this
        [xcoord, ycoord, field_value] = ['', '', pointdf['Natur_type'][count]]
        count+=1
        coords = i
        pt = map(float, coords[1:-1].split(','))
        xcoord, ycoord = float(pt[0]), float(pt[1])
        # Get properties and build field values here
        if xcoord and ycoord and field_value:
            feature = ogr.Feature(p_layer.GetLayerDefn())
            feature.SetField('fld_a', field_value)

            wkt = "POINT ({} {})".format(xcoord, ycoord)
            point = ogr.CreateGeometryFromWkt(wkt)
            feature.SetGeometry(point)
            p_layer.CreateFeature(feature)
            feature = None
            [xcoord, ycoord, field_value] = ['', '', '']
    return pointshapefilepath

def create_poly_shape():
    #prep files
    driver = ogr.GetDriverByName("ESRI Shapefile")
    shapefilepath = "/Data/area.shp"
    area_data_source = driver.CreateDataSource(shapefilepath)

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(32633)

    # Area shapefile setup
    a_layer = area_data_source.CreateLayer("area_layer", None, ogr.wkbPolygon)
    field_testfield = ogr.FieldDefn("fld_a", ogr.OFTString)
    field_testfield.SetWidth(50)
    a_layer.CreateField(field_testfield)

    # Do the json reading
    data = pd.read_json("/Data/dlfile.json", orient='records', lines=True)
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
    count = 0
    for i in df3[0]:
        # geo_type = geo.get('type')

        # elif geo_type == 'Polygon':  # Or if it's a polygon, do this
        [poly, field_value] = ['', df3[1][count]]
        count+=1
        #print i
        polycoords = i
        poly = create_polygon(polycoords)
        if poly and field_value:
            feature = ogr.Feature(a_layer.GetLayerDefn())
            feature.SetField('fld_a', field_value) # Setting field value for each polygon

            # wkt = "Polygon ({})".format(poly)
            area = ogr.CreateGeometryFromWkt(poly)
            feature.SetGeometry(area)
            a_layer.CreateFeature(feature)
            feature = None
            [poly, field_value] = ['', '']
        else:
            print('Could not discern geometry')

    return shapefilepath

# pointdf = pd.read_csv("typeprediction.csv")
# create_point_shape(pointdf)