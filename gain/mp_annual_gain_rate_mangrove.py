### Creates tiles of annual aboveground biomass gain rates for mangroves using IPCC Wetlands Supplement Table 4.4 rates.
### Its inputs are the continent-ecozone tiles, mangrove biomass tiles (for locations of mangroves), and the IPCC
### gain rate table.

from multiprocessing.pool import Pool
from functools import partial
import annual_gain_rate_mangrove
import pandas as pd
import subprocess
import os
import sys
sys.path.append('../')
import constants_and_names as cn
import universal_util as uu

pd.options.mode.chained_assignment = None

# Lists the mangrove biomass tiles instead of the general tree biomass tiles because
# there are many fewer mangrove biomass tiles (88 vs 315)
# mangrove_biomass_tile_list = uu.tile_list(cn.mangrove_biomass_2000_dir)
# mangrove_biomass_tile_list = ['20S_110E', '30S_110E'] # test tiles
mangrove_biomass_tile_list = ['10N_080W'] # test tiles
print mangrove_biomass_tile_list
print "There are {} tiles to process".format(str(len(mangrove_biomass_tile_list)))

# For downloading all tiles in the input folders
download_list = [cn.cont_eco_dir, cn.mangrove_biomass_2000_dir]

# for input in download_list:
#     uu.s3_folder_download('{}'.format(input), '.')

# For copying individual tiles to spot machine for testing
for tile in mangrove_biomass_tile_list:

    uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.cont_eco_dir, tile, cn.pattern_cont_eco_processed), '.')    # continents and FAO ecozones 2000
    uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.mangrove_biomass_2000_dir, tile, cn.pattern_mangrove_biomass_2000), '.')         # mangrove aboveground biomass

# Table with IPCC Wetland Supplement Table 4.4 default mangrove gain rates
cmd = ['aws', 's3', 'cp', os.path.join(cn.gain_spreadsheet_dir, cn.gain_spreadsheet), '.']
subprocess.check_call(cmd)

# Imports the table with the ecozone-continent codes and the carbon gain rates
gain_table = pd.read_excel("{}".format(cn.gain_spreadsheet),
                           sheet_name = "mangrove gain, for model")

# Removes rows with duplicate codes (N. and S. America for the same ecozone)
gain_table_simplified = gain_table.drop_duplicates(subset='gainEcoCon', keep='first')

type_ratio_dict = {'1': cn.below_to_above_trop_dry_mang, '2':cn.below_to_above_trop_wet_mang, '3': cn.below_to_above_subtrop_mang}
type_ratio_dict = {int(k):float(v) for k,v in type_ratio_dict.items()}

gain_table_simplified['BGB_AGB_ratio'] = gain_table_simplified['forestType'].map(type_ratio_dict)

gain_table_simplified['BGB_annual_rate'] = gain_table_simplified.gain_tons_yr * gain_table_simplified.BGB_AGB_ratio
print gain_table_simplified.head(5)

# Converts the continent-ecozone codes and corresponding gain rates to a dictionary
gain_above_dict = pd.Series(gain_table_simplified.gain_tons_yr.values,index=gain_table_simplified.gainEcoCon).to_dict()

gain_below_dict = pd.Series(gain_table_simplified.BGB_annual_rate.values,index=gain_table_simplified.gainEcoCon).to_dict()

# Adds a dictionary entry for where the ecozone-continent code is 0 (not in a continent)
gain_above_dict[0] = 0
gain_below_dict[0] = 0

# Converts all the keys (continent-ecozone codes) to float type
gain_above_dict = {float(key): value for key, value in gain_above_dict.iteritems()}
gain_below_dict = {float(key): value for key, value in gain_below_dict.iteritems()}

# This configuration of the multiprocessing call is necessary for passing multiple arguments to the main function
# It is based on the example here: http://spencerimp.blogspot.com/2015/12/python-multiprocess-with-multiple.html
# This script didn't work calling 16 processors on an m4.16xlarge because when it tried uploading the output tiles to s3
# simultaneously (the first set of tiles finished simultaneously) it couldn't upload them, perhaps because the upload channel got clogged.
# So I tried using 8 processors instead, which works. I don't know what the highest number of processors would be.
num_of_processes = 16
pool = Pool(num_of_processes)
pool.map(partial(annual_gain_rate_mangrove.annual_gain_rate, gain_above_dict=gain_above_dict, gain_below_dict=gain_below_dict), mangrove_biomass_tile_list)
pool.close()
pool.join()

# # For single processor use
# for tile in mangrove_biomass_tile_list:
#
#     annual_gain_rate_mangrove.annual_gain_rate(tile, gain_table_dict)

uu.upload_final_set(cn.annual_gain_AGB_mangrove_dir, cn.pattern_annual_gain_AGB_mangrove)
uu.upload_final_set(cn.annual_gain_BGB_mangrove_dir, cn.pattern_annual_gain_BGB_mangrove)

