from osgeo import gdal

def gdalMask(rasterpath):
    vector_layer = "area.shp"
    raster_layer = rasterpath
    target_layer = rasterpath+"mask.tif"

    # open the raster layer and get its relevant properties
    raster_ds = gdal.Open(raster_layer, gdal.GA_ReadOnly)
    xSize = raster_ds.RasterXSize
    ySize = raster_ds.RasterYSize
    geotransform = raster_ds.GetGeoTransform()
    projection = raster_ds.GetProjection()

    # create the target layer (1 band)
    driver = gdal.GetDriverByName('GTiff')
    target_ds = driver.Create(target_layer, xSize, ySize, bands = 1, eType = gdal.GDT_Byte, options = ["COMPRESS=DEFLATE"])
    target_ds.SetGeoTransform(geotransform)
    target_ds.SetProjection(projection)

    # rasterize the vector layer into the target one
    ds = gdal.Rasterize(target_ds, vector_layer)

    target_ds = None
    return target_layer

gdalMask("NaturalColorwithDRA.tiff")