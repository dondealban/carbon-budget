### This script assigns annual above and belowground biomass gain rates (in the units of IPCC Table 4.9 (currently tonnes
### biomass/ha/yr)) to non-mangrove natural forest pixels.
### The inputs are continent-ecozone tiles and natural forest age category tiles, as well as IPCC Table 4.9, formatted
### for easy ingestion by pandas.
### Essentially, this does some processing of the IPCC gain rate table, then uses it as a dictionary that it applies
### to every pixel in every tile.
### Each continent-ecozone-forest age category combination gets its own code, which matches the codes in the
### processed IPCC table.
### Belowground biomass gain rate is a constant proportion of aboveground biomass gain rate, again according to IPCC tables.

import utilities
import datetime
import numpy as np
import rasterio
import subprocess
import os
import sys
sys.path.append('../')
import constants_and_names as cn

# Necessary to suppress a pandas error later on
np.set_printoptions(threshold=np.nan)

def annual_gain_rate(tile_id, gain_table_dict):

    # Converts the forest age category decision tree output values to the three age categories--
    # 10000: primary forest; 20000: secondary forest > 20 years; 30000: secondary forest <= 20 years
    # These are five digits so they can easily be added to the four digits of the continent-ecozone code to make unique codes
    # for each continent-ecozone-age combination.
    # The key in the dictionary is the forest age category decision tree endpoints.
    age_dict = {0: 0, 1: 20000, 2: 20000, 3: 10000, 4: 30000, 5: 20000, 6: 10000, 7: 30000, 8: 30000, 9: 30000, 10: 30000}

    print "Processing:", tile_id

    # Start time
    start = datetime.datetime.now()

    # Names of the forest age category, continent-ecozone, and mangrove biomass tiles
    age_cat = '{0}_{1}.tif'.format(tile_id, cn.pattern_age_cat_natrl_forest)
    cont_eco = '{0}_{1}.tif'.format(tile_id, cn.pattern_cont_eco_processed)

    # Name of the output natural forest gain rate tile, before mangroves are masked out
    AGB_gain_rate_unmasked = '{0}_unmasked_{1}.tif'.format(tile_id, cn.pattern_annual_gain_AGB_natrl_forest)

    # Name of the output natural forest gain rate tile, with mangroves masked out
    AGB_gain_rate = '{0}_{1}.tif'.format(tile_id, cn.pattern_annual_gain_AGB_natrl_forest)

    print "  Reading input files and creating aboveground biomass gain rate for {}".format(tile_id)

    # Opens continent-ecozone tile
    with rasterio.open(cont_eco) as cont_eco_src:

        # Grabs metadata about the tif, like its location/projection/cellsize
        kwargs = cont_eco_src.meta

        # Grabs the windows of the tile (stripes) to iterate over the entire tif without running out of memory
        windows = cont_eco_src.block_windows(1)

        # Opens age category tile
        with rasterio.open(age_cat) as age_cat_src:

            # Updates kwargs for the output dataset.
            # Need to update data type to float 32 so that it can handle fractional gain rates
            kwargs.update(
                driver='GTiff',
                count=1,
                compress='lzw',
                nodata=0,
                dtype='float32'
            )

            # Opens the output aboveground biomass gain rate tile, giving it the arguments of the input tiles
            with rasterio.open(AGB_gain_rate_unmasked, 'w', **kwargs) as dst_above:

                # Iterates across the windows (1 pixel strips) of the input tile
                for idx, window in windows:

                    # Creates windows for each input raster
                    cont_eco = cont_eco_src.read(1, window=window)
                    age_cat = age_cat_src.read(1, window=window)

                    # Recodes the input forest age category array with 10 different values into the 3 actual age categories
                    age_recode = np.vectorize(age_dict.get)(age_cat)

                    # Adds the age category codes to the continent-ecozone codes to create an array of unique continent-ecozone-age codes
                    cont_eco_age = cont_eco + age_recode

                    # Converts the continent-ecozone-age array to float so that the values can be replaced with fractional gain rates
                    cont_eco_age = cont_eco_age.astype('float32')

                    # Creates a new array which will have the annual aboveground gain rates
                    gain_rate_AGB = cont_eco_age

                    # Applies the dictionary of continent-ecozone-age gain rates to the continent-ecozone-age array to
                    # get annual gain rates (metric tons aboveground biomass/yr) for each pixel
                    for key, value in gain_table_dict.iteritems():
                        gain_rate_AGB[gain_rate_AGB  == key] = value

                    # Writes the output window to the output
                    dst_above.write_band(1, gain_rate_AGB , window=window)

    if os.path.exists('{0}_{1}.tif'.format(tile_id, cn.pattern_mangrove_biomass_2000)):

        # Aboveground mangrove biomass tile
        mangrove_biomass = '{0}_{1}.tif'.format(tile_id, cn.pattern_mangrove_biomass_2000)

        # Mangrove biomass tiles that have the nodata pixels removed
        mangrove_reclass = '{0}_reclass_{1}.tif'.format(tile_id, cn.pattern_mangrove_biomass_2000)

        # Removes the nodata values in the mangrove biomass rasters because having nodata values in the mangroves didn't work
        # in gdal_calc. The gdal_calc expression didn't know how to evaluate nodata values, so I had to remove them.
        print "  Removing nodata values in mangrove biomass raster {}".format(tile_id)
        cmd = ['gdal_translate', '-a_nodata', 'none', mangrove_biomass, mangrove_reclass]
        subprocess.check_call(cmd)

        # Masks out the mangrove biomass from the natural forest gain rate
        # Ideally this would be part of the rasterio/numpy operation (not its own gdal operation later) but I couldn't
        # figure out how to get the mask working in numpy for some reason
        print "  Masking mangroves from aboveground gain rate for tile {}".format(tile_id)
        mangrove_mask_calc = '--calc=A*(B==0)'
        mask_outfilename = AGB_gain_rate
        mask_outfilearg = '--outfile={}'.format(mask_outfilename)
        cmd = ['gdal_calc.py', '-A', AGB_gain_rate_unmasked, '-B', mangrove_reclass, mangrove_mask_calc, mask_outfilearg,
               '--NoDataValue=0', '--overwrite', '--co', 'COMPRESS=LZW']
        subprocess.check_call(cmd)

        utilities.upload_final(cn.annual_gain_AGB_natrl_forest_dir, tile_id, cn.pattern_annual_gain_AGB_natrl_forest)

    else:

        os.rename('{0}_unmasked_{1}.tif'.format(tile_id, cn.pattern_annual_gain_AGB_natrl_forest),
                  '{0}_{1}.tif'.format(tile_id, cn.pattern_annual_gain_AGB_natrl_forest))

        utilities.upload_final(cn.annual_gain_AGB_natrl_forest_dir, tile_id, cn.pattern_annual_gain_AGB_natrl_forest)


    # Calculates belowground biomass rate from aboveground biomass rate
    print "  Creating belowground biomass gain rate for tile {}".format(tile_id)
    above_to_below_calc = '--calc=(A>0)*A*{}'.format(cn.below_to_above_natrl_forest)
    below_outfilename = '{0}_{1}.tif'.format(tile_id, cn.pattern_annual_gain_BGB_natrl_forest)
    below_outfilearg = '--outfile={}'.format(below_outfilename)
    cmd = ['gdal_calc.py', '-A', AGB_gain_rate, above_to_below_calc, below_outfilearg,
           '--NoDataValue=0', '--overwrite', '--co', 'COMPRESS=LZW']
    subprocess.check_call(cmd)

    utilities.upload_final(cn.annual_gain_BGB_natrl_forest_dir, tile_id, cn.pattern_annual_gain_BGB_natrl_forest)

    end = datetime.datetime.now()
    elapsed_time = end-start

    print "  Processing time for tile", tile_id, ":", elapsed_time