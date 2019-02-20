import ogr, gdal

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
    yBottom = yTop+(rows*pixelHeight)

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

