from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from osgeo import gdal, gdalnumeric, ogr, osr
import os, sys
import struct
import pandas as pd
import csv
from affine import Affine
import req
# import VIRF # This module should be brought here!
import shapefilecrop
import pointWithinPolygon

conf = SparkConf().setAppName('Spark-rst1.py').setMaster('local[2]')
sc = SparkContext(conf=conf)
spark = SparkSession.builder \
    .master('local[2]') \
    .appName('Spark-rst1.py') \
    .config(conf=SparkConf()) \
    .getOrCreate()

# Calculating RGB pixel value from R, G and B
def getRGB(df, fn):
    df[fn + ' RGB'] = (65536 * df.R) + (256 * df.G) + df.B
    return df[fn + ' RGB']

# Function to get raster file path, number of rasters as lenght, name of the raster function and the shapefile path of
# the training dataset
def rasterfile_path(arg2, arg3, arg4, arg5):
    rasterpath, lenght, fnlist, shapefilepath = req.get_request(arg2, arg3, arg4, arg5) # passing variables are the
    # bbox coordinates
    return rasterpath, lenght, fnlist, shapefilepath

def world2Pixel(geoMatrix, x, y):
    """
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate
    """
    # print(x)
    # print(y)
    ulX = geoMatrix[0] # maxx
    # print(ulX)
    ulY = geoMatrix[3] # miny
    # print(ulY)
    xDist = geoMatrix[1] # pixel width
    # print(xDist)
    yDist = geoMatrix[5] # pixel height
    # print(yDist)
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]
    pixel = int((x - ulX) / xDist)
    line = int((y - ulY) / yDist)

    return (pixel, line)

# Creating training dataset
def training_dataset(shapefile_path, raster_path, fn):
    srcImage = gdal.Open(raster_path) # opening raster file
    geoTrans = srcImage.GetGeoTransform()
    mylist1 = list()
    # Create an OGR layer from a boundary shapefile
    shapef = ogr.Open(shapefile_path)
    lyr = shapef.GetLayer()
    # print "Geometry has %i geometries" % (lyr.GetFeatureCount())

    # Convert the layer extent to image pixel coordinates
    # mylist = list()
    typelist = list()
    for feat in lyr:
        mylist = list()
        if shapefilecrop.shape_crop(feat, lyr): # check that the point lies in the bbox
            # print 'yes'
            for band in range(1, 4):
                # print('Band:', band)
                rb = srcImage.GetRasterBand(band)
                field = feat.GetField("fld_a")
                typelist.append(field)
                geom = feat.GetGeometryRef()
                # print geom
                if geom != None:
                    mx, my = geom.GetX(), geom.GetY()
                ulX, ulY = world2Pixel(geoTrans, mx, my)
                intval = rb.ReadAsArray(ulX, ulY, 1, 1)
                # print intval[0]
                mylist.extend(intval[0])
        else:
            print 'No'
        mylist1.append(mylist)
    df = pd.DataFrame(mylist1) # create dataframe to store R,G & B values
    # df = df.transpose()
    df.columns = ['R', 'G', 'B']
    df.to_csv('testcsv.csv')
    df[fn + ' RGB'] = getRGB(df, fn)
    df = df.drop(['R', 'G', 'B'], axis=1) # remove R, G & B columns
    column_values = pd.Series(typelist) # name of Nature_type

    return df, column_values

# Creating prediction dataset
def prediction_dataset(raster_path, fn):
    srcImage = gdal.Open(raster_path)
    geoTrans = srcImage.GetGeoTransform()
    mylist1 = list()
    T0 = Affine.from_gdal(*srcImage.GetGeoTransform())
    cols = srcImage.RasterYSize
    rows = srcImage.RasterXSize
    T1 = T0 * Affine.translation(0.5, 0.5)
    rc2xy = lambda r, c: (c, r) * T1 # Convert row and column to xy coordinates
    pointlist = []
    for i in range(cols):
        for j in range(rows):
            pointlist.append(rc2xy(i, j))

    # Convert the layer extent to image pixel coordinates
    # mylist = list()
    # typelist = list()
    polylist = pointWithinPolygon.poly_contain()
    for feat in pointlist:
        mylist = list()
        # point = ogr.Geometry(ogr.wkbPoint)
        # point.AddPoint(feat[0],feat[1])
        # point.ExportToWkb()
        # for poly in polylist:
            #if poly.Contains(point):
        for band in range(1, 4):
            rb = srcImage.GetRasterBand(band)
            geom = feat
            # print geom
            if geom != None:
                mx, my = geom[0], geom[1]
                # print mx,my
            ulX, ulY = world2Pixel(geoTrans, mx, my)
            # print ulX, ulY
            while ulY < srcImage.RasterYSize:
                intval = rb.ReadAsArray(ulX, ulY, 1, 1)
                mylist.extend(intval[0])
                # print feat
                break
        mylist1.append(mylist)
    df = pd.DataFrame(mylist1)
    # df = df.transpose()
    df.columns = ['R', 'G', 'B']
    df[fn + ' RGB'] = getRGB(df, fn)
    df = df.drop(['R', 'G', 'B'], axis=1)

    return df, pointlist


def main(arg2, arg3, arg4, arg5):
    trainingdflist = []
    trainingrasterpath, lenght, fnlist, shapefile_path = rasterfile_path(arg2, arg3, arg4, arg5)
    print 'Creating Training Dataset...'
    for i in range(lenght):
        trainingdf, column_values = training_dataset(shapefile_path, trainingrasterpath[i], fnlist[i])
        trainingdflist.append(trainingdf)
    trainingfinaldf = pd.concat(trainingdflist, axis=1)
    trainingfinaldf = pd.DataFrame(trainingfinaldf)
    trainingfinaldf.insert(loc=0, column='NATYP_ID', value=column_values)
    trainingfinaldf.to_csv("/Data/trainingfinalRGB.csv")
    print 'Dataset Created...'

    predeictiondflist = []
    print 'Creating Prediction Dataset...'
    for j in range(lenght):
        predictiondf, pointlist = prediction_dataset(trainingrasterpath[j], fnlist[j])
        predeictiondflist.append(predictiondf)
    predictionfinaldf = pd.concat(predeictiondflist, axis=1)
    predictionfinaldf = pd.DataFrame(predictionfinaldf)
    predictionfinaldf["Point"] = pointlist
    # print len(pointlist)
    predictionfinaldf = predictionfinaldf[(predictionfinaldf.iloc[:, 1:-2] != 0).any(axis=1)].reset_index(drop=True)
    predictionfinaldf = pd.DataFrame(predictionfinaldf)
    predictionfinaldf.to_csv("/Data/predictionfinalRGB.csv")
    print 'Prediction Dataset Created...'

    VIRF.training_model() # calling Random forest


if __name__ == '__main__':

    #
    # example run : $ python rst1.py /<full-path>/<shapefile-name>.shp
    #
    if len(sys.argv) < 4:
        print("[ ERROR ] you must provide one arg. 1) the full shapefile path 2) and 4 bbox values")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

