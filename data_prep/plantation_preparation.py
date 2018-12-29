
import subprocess
import os
import psycopg2
from osgeo import gdal
import sys
sys.path.append('../')
import constants_and_names
import universal_util

def rasterize_gadm_1x1(tile_id):

    print "Getting bounding coordinates for tile", tile_id
    xmin, ymin, xmax, ymax = universal_util.coords(tile_id)
    print "  xmin:", xmin, "; xmax:", xmax, "; ymin", ymin, "; ymax:", ymax

    # Degrees of tile in x and y dimensions
    x_size = abs(int(xmin) - int(xmax))
    y_size = abs(int(ymin) - int(ymax))

    # Iterates through tile by 1x1 degree
    for x in range(x_size):

        xmin_1x1 = int(xmin) + x
        xmax_1x1 = int(xmin) + x + 1

        for y in range(y_size):

            ymin_1x1 = int(ymin) + y
            ymax_1x1 = int(ymin) + y + 1

            # print "  xmin_1x1:", xmin_1x1, "; xmax_1x1:", xmax_1x1, "; ymin_1x1", ymin_1x1, "; ymax_1x1:", ymax_1x1

            tile_1x1 = '{0}_{1}_GADM.tif'.format(ymax_1x1, xmin_1x1)
            cmd = ['gdal_rasterize', '-tr', constants_and_names.Hansen_res, constants_and_names.Hansen_res, '-co', 'COMPRESS=LZW',
                   constants_and_names.gadm_shp, tile_1x1, '-te', xmin_1x1, ymin_1x1, xmax_1x1, ymax_1x1, '-a', '1', '-a_nodata,' '0']
            subprocess.check_call(cmd)

            print "Checking if {} contains any data...".format(tile_1x1)
            stats = universal_util.check_for_data(tile_1x1)

            if stats[1] > 0:
                print "  Data found in {}. Keeping tile".format(tile_1x1)

            else:
                print "  No data found in {}. Deleting.".format(tile_1x1)
                os.remove(tile_1x1)

# Creates a list of 1x1 degree tiles, with the defining coordinate in the northwest corner
def create_1x1_tiles(tile_id):

    print "Getting bounding coordinates for tile", tile_id
    xmin, ymin, xmax, ymax = universal_util.coords(tile_id)
    print "  xmin:", xmin, "; xmax:", xmax, "; ymin", ymin, "; ymax:", ymax

    # Degrees of tile in x and y dimensions
    x_size = abs(int(xmin) - int(xmax))
    y_size = abs(int(ymin) - int(ymax))

    # Iterates through tile by 1x1 degree
    for x in range(x_size):

        xmin_1x1 = int(xmin) + x
        xmax_1x1 = int(xmin) + x + 1

        for y in range(y_size):

            ymin_1x1 = int(ymin) + y
            ymax_1x1 = int(ymin) + y + 1

            # print "  xmin_1x1:", xmin_1x1, "; xmax_1x1:", xmax_1x1, "; ymin_1x1", ymin_1x1, "; ymax_1x1:", ymax_1x1

            tile_1x1 = '{0}_{1}'.format(ymax_1x1, xmin_1x1)

            # Adds the new 1x1 degree tile to the list of 1x1 degree tiles
            list_1x1.append(tile_1x1)

            # https://gis.stackexchange.com/questions/187224/how-to-use-gdal-rasterize-with-postgis-vector

            # cmd = ['gdal_rasterize', '-tr', constants_and_names.Hansen_res, constants_and_names.Hansen_res, '-co', 'COMPRESS=LZW', 'PG:dbname=ubuntu', '-l', 'all_plant', '{0}_{1}_plant.tif'.format(ymax_1x1, xmax_1x1), '-te', xmin_1x1, ymin_1x1, xmax_1x1, ymax_1x1, '-a', 'growth', '-a_nodata,' '0']
            #
            # subprocess.check_call(cmd)

            # gdal_rasterize -tr 0.00025 0.00025 -co COMPRESS=LZW PG:"dbname=ubuntu" -l all_plant col_plant_gdalrasterize.tif -te -80 0 -70 10 -a growth -a_nodata 0

            # # https://gis.stackexchange.com/questions/30267/how-to-create-a-valid-global-polygon-grid-in-postgis
            # # https://stackoverflow.com/questions/48978616/best-way-to-run-st-intersects-on-features-inside-one-table
            # # https://postgis.net/docs/ST_Intersects.html
            # SELECT * INTO test_table FROM all_plant WHERE ST_Intersects(all_plant.wkb_geometry, ST_GeogFromText('POLYGON((-80 0,-79 0,-79 -1,-80 -1,-80 0))'))
