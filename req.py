from requests.packages.urllib3.util import retry
from requests import adapters
import requests
import os.path
import createpoly
import getCentroid
import gdalMask

# Function to extract filename from link
def get_filename(rf):

    fn = rf.rsplit('%22')[3]
    fn_full = fn.rsplit('%20')
    return ''.join(fn_full)

# Function to get number of rendering rules
def get_lenght(rl):

    return len(rl)

# function to query Api with connection abort handling
def query_api(full_url):
    session = requests.Session()
    for scheme in ('http://', 'https://'):
         session.mount(scheme, adapters.HTTPAdapter(
             max_retries=retry.Retry(connect=5),
         ))

    r_s = session.get(full_url)
    return r_s

# Function to download raster files and training data json file
def get_request(xLeftyTop, xLeftyBottom, xRightyBottom, xRightyTop):

    # -60408.7174,6480321.3102,97041.3008,6583207.7367
    url1 = "https://arcgisproxy.miljodirektoratet.no/arcgis/rest/services/naturtyper_dn/MapServer/1/query?" \
           "geometry={bbox}&geometryType=esriGeometryEnvelope&outFields=Naturtype&returnGeometry=True&f=json&" \
           "MaxRecordCount={recordCount}&spatialRel=esriSpatialRelContains"
    full_url1 = url1.format(
        bbox=str(xLeftyTop) + "%2C" + str(xLeftyBottom) + "%2C" + str(xRightyBottom) + "%2C" + str(xRightyTop),
        recordCount=100)
    rss = query_api(full_url1)
    open('dlfile.json', 'wb').write(rss.content)
    #create polygon shapefile from downloaded json file
    polygonshapefilepath = createpoly.create_poly_shape() # Calling function to create polygon shapefile from training
    # dataset json downloaded from miljodirektorat Api
    shapefilepath = getCentroid.main(polygonshapefilepath) # Calling function to create shapefile of centroids of
    # polygon shapefile

    # Raster URL
    url = 'https://services3.geodataonline.no/arcgis/rest/services/Geomap_UTM33_EUREF89/GeomapSentinel/' \
          'ImageServer/exportImage?f=image&format=tiff&bandIds=&renderingRule={rasterFunction}&bbox={bbox}&' \
          'imageSR=32633&bboxSR=32633&size={size}'
    with open('/Data/renderingrule.txt') as f:
        renderingRuleList = [line.rstrip('\n') for line in f]
    # print renderingRuleList
    lenght = get_lenght(renderingRuleList)
    rasterpath = []
    fnlist = []
    for i in range(lenght):
        # -2259786.4167301673%2C6063679.814029297%2C3679084.1276775887%2C8279918.913174162
        # size="1096%2C409"
        full_url = url.format(rasterFunction=renderingRuleList[i], size="3288%2C1227",
                            bbox=str(xLeftyTop)+"%2C"+str(xLeftyBottom)+"%2C"+str(xRightyBottom)+"%2C"+str(xRightyTop))
        # print full_url
        fn = get_filename(renderingRuleList[i])
        if not os.path.isfile(fn+'.tiff'):
            print('Downloading...')
            r = query_api(full_url)
            open(fn+'.tiff', 'wb').write(r.content)
        rasterpathitem = fn+'.tiff'
        print(fn+' Response')
        gdalMask.gdalMask(rasterpathitem)
        rasterpath.append(rasterpathitem)
        fnlist.append(fn)

    return rasterpath, lenght, fnlist, shapefilepath

# get_request(-60408.7174,6480321.3102,97041.3008,6583207.7367)
