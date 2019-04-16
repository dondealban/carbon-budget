import create_carbon_pools_in_emis_year
from multiprocessing.pool import Pool
from functools import partial
import subprocess
import os
import pandas as pd
import sys
sys.path.append('../')
import constants_and_names as cn
import universal_util as uu

pd.options.mode.chained_assignment = None

# tile_list = uu.tile_list(cn.AGC_emis_year_dir)
# tile_list = ['00N_110E'] # test tiles
tile_list = ['80N_020E', '00N_020E', '00N_000E', '00N_110E'] # test tiles
print tile_list
print "There are {} tiles to process".format(str(len(tile_list)))

# For downloading all tiles in the input folders.
input_files = [
    cn.AGC_emis_year_dir,
    cn.WHRC_biomass_2000_unmasked_dir,
    cn.mangrove_biomass_2000_dir,
    cn.cont_eco_dir,
    cn.bor_tem_trop_processed_dir,
    cn.precip_processed_dir,
    cn.soil_C_2000_dir,
    cn.elevation_processed_dir
    ]

# for input in input_files:
#     uu.s3_folder_download('{}'.format(input), '.')

# For copying individual tiles to spot machine for testing.
for tile in tile_list:

    uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.AGC_emis_year_dir, tile,
                                                            cn.pattern_AGC_emis_year), '.')
    uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.WHRC_biomass_2000_unmasked_dir, tile,
                                                            cn.pattern_WHRC_biomass_2000_unmasked), '.')
    uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.cont_eco_dir, tile,
                                                            cn.pattern_cont_eco_processed), '.')
    uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.fao_ecozone_processed_dir, tile,
                                                            cn.pattern_fao_ecozone_processed), '.')
    uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.precip_processed_dir, tile,
                                                            cn.pattern_precip), '.')
    uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.soil_C_2000_dir, tile,
                                                            cn.pattern_soil_C_2000), '.')
    uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.elevation_processed_dir, tile,
                                                            cn.pattern_elevation), '.')
    try:
        uu.s3_file_download('{0}{1}_{2}.tif'.format(cn.mangrove_biomass_2000_dir, tile, cn.pattern_mangrove_biomass_2000), '.')
    except:
        print "No mangrove biomass in", tile


# Table with IPCC Wetland Supplement Table 4.4 default mangrove gain rates
cmd = ['aws', 's3', 'cp', os.path.join(cn.gain_spreadsheet_dir, cn.gain_spreadsheet), '.']
subprocess.check_call(cmd)

# Imports the table with the ecozone-continent codes and the carbon gain rates
gain_table = pd.read_excel("{}".format(cn.gain_spreadsheet),
                           sheet_name = "mangrove gain, for model")

# Removes rows with duplicate codes (N. and S. America for the same ecozone)
gain_table_simplified = gain_table.drop_duplicates(subset='gainEcoCon', keep='first')

mang_BGB_AGB_ratio = create_carbon_pools_in_emis_year.mangrove_pool_ratio_dict(gain_table_simplified,
                                                                           cn.below_to_above_trop_dry_mang,
                                                                           cn.below_to_above_trop_wet_mang,
                                                                           cn.below_to_above_subtrop_mang)

mang_deadwood_AGB_ratio = create_carbon_pools_in_emis_year.mangrove_pool_ratio_dict(gain_table_simplified,
                                                                           cn.deadwood_to_above_trop_dry_mang,
                                                                           cn.deadwood_to_above_trop_wet_mang,
                                                                           cn.deadwood_to_above_subtrop_mang)

mang_litter_AGB_ratio = create_carbon_pools_in_emis_year.mangrove_pool_ratio_dict(gain_table_simplified,
                                                                           cn.litter_to_above_trop_dry_mang,
                                                                           cn.litter_to_above_trop_wet_mang,
                                                                           cn.litter_to_above_subtrop_mang)

print "Creating carbon pools..."

num_of_processes = 16
pool = Pool(num_of_processes)
pool.map(partial(create_carbon_pools_in_emis_year.create_BGC, mang_deadwood_AGB_ratio=mang_deadwood_AGB_ratio), tile_list)
pool.close()
pool.join()

num_of_processes = 16
pool = Pool(num_of_processes)
pool.map(partial(create_carbon_pools_in_emis_year.create_deadwood, mang_deadwood_AGB_ratio=mang_deadwood_AGB_ratio), tile_list)
pool.close()
pool.join()

num_of_processes = 16
pool = Pool(num_of_processes)
pool.map(partial(create_carbon_pools_in_emis_year.create_litter, mang_litter_AGB_ratio=mang_litter_AGB_ratio), tile_list)
pool.close()
pool.join()

# # For single processor use
# for tile in tile_list:
#     create_carbon_pools_in_emis_year.create_BGC(tile, mang_BGB_AGB_ratio)
#     create_carbon_pools_in_emis_year.create_deadwood(tile, mang_deadwood_AGB_ratio)
#     create_carbon_pools_in_emis_year.create_litter(tile, mang_litter_AGB_ratio)

print "Uploading output to s3..."

# uu.upload_final_set('{0}/{1}/'.format(cn.AGC_dir, type), '{0}_{1}'.format(cn.pattern_AGC, type))
uu.upload_final_set(cn.BGC_emis_year_dir, cn.pattern_BGC_emis_year)
uu.upload_final_set(cn.deadwood_emis_year_2000_dir, cn.pattern_deadwood_emis_year_2000)
uu.upload_final_set(cn.litter_emis_year_2000_dir, cn.pattern_litter_emis_year_2000)
# uu.upload_final_set('{0}/{1}/'.format(cn.soil_C_pool_dir, type), '{0}_{1}'.format(cn.pattern_soil_pool, type))
# uu.upload_final_set('{0}/{1}/'.format(cn.total_C_dir, type), '{0}_{1}'.format(cn.pattern_total_C, type))