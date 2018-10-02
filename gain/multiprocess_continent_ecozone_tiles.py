### Creates tiles in which each pixel is a combination of the continent and FAO FRA 2000 ecozone.
### The tiles are based on a shapefile which combines the FAO FRA 2000 ecozone shapefile and a continent shapefile.
### The FAO FRA 2000 shapefile is from http://www.fao.org/geonetwork/srv/en/resources.get?id=1255&fname=eco_zone.zip&access=private
### The continent shapefile is from https://www.baruch.cuny.edu/confluence/display/geoportal/ESRI+International+Data
### Various processing steps in ArcMap were used to make sure that the entirety of the ecozone shapefile had
### continents assigned to it. The creation of the continent-ecozone shapefile was done in ArcMap.
### In the resulting ecozone-continent shapefile, the final field has continent and ecozone concatenated.
### That ecozone-continent field can be parsed to get the ecozone and continent for every pixel,
### which are necessary for assigning gain rates to pixels.
### This script also breaks the input tiles into windows that are 512x512 pixels and assigns all pixels that
### don't have a continent-ecozone code to the most common code in that window.
### This is done to expand the extent of the continent-ecozone tiles to include pixels that don't have a continent-ecozone
### code because they are just outside the original shapefile.
### It is necessary to expand the continent-ecozone codes into those nearby areas because otherwise some forest age category
### pixels are outside the continent-ecozone pixels and can't have gain rates assigned to them.
### This maneuver provides the necessary continent-ecozone information to assign gain rates.


import multiprocessing
import utilities
import continent_ecozone_tiles
import subprocess

### sudo pip install rasterio --upgrade
### sudo pip install scipy

# Ecozone shapefile location and file
cont_ecozone_dir = 's3://gfw2-data/climate/carbon_model/fao_ecozones/'
cont_ecozone = 'fao_ecozones_fra_2000_continents_assigned_dissolved_FINAL_20180906.zip'

# Downloads ecozone shapefile
utilities.s3_file_download('{0}{1}'.format(cont_ecozone_dir, cont_ecozone), '.', )

# Unzips ecozone shapefile
cmd = ['unzip', cont_ecozone]
subprocess.check_call(cmd)

# Location of the biomass tiles, used for ecozone-continent tile boundaries
biomass_dir = 's3://gfw2-data/climate/WHRC_biomass/WHRC_V4/Processed/'

biomass_tile_list = utilities.tile_list(biomass_dir)
# biomass_tile_list = ["00N_000E", "00N_050W", "00N_060W", "00N_010E", "00N_020E", "00N_030E", "00N_040E", "10N_000E", "10N_010E", "10N_010W", "10N_020E", "10N_020W"] # test tiles
# biomass_tile_list = ['20S_110E'] # test tile
print biomass_tile_list

# For multiprocessor use
count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(processes=count/4)
pool.map(continent_ecozone_tiles.create_continent_ecozone_tiles, biomass_tile_list)

# # For single processor use
# for tile in biomass_tile_list:
#
#     continent_ecozone_tiles.create_continent_ecozone_tiles(tile)