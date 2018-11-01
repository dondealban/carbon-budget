import subprocess
import glob

biomass_to_c = 0.5

above_to_below_natrl_forest = 0.26
above_to_below_natrl_forest = 0.608

# Spreadsheet with annual gain rates
gain_spreadsheet = 'gain_rate_continent_ecozone_age_20181017.xlsx'

# Woods Hole biomass 2000 version 4 tiles
biomass_dir = 's3://gfw2-data/climate/WHRC_biomass/WHRC_V4/Processed/'

# Lola Fatoyinbo aboveground mangrove biomass tiles
pattern_mangrove_biomass = 'mangrove_agb_t_ha'
mangrove_biomass_dir = 's3://gfw2-data/climate/carbon_model/mangrove_biomass/processed/20181019/'

# Annual Hansen loss tiles (2001-2015)
loss_dir = 's3://gfw2-data/forest_change/hansen_2015/Loss_tiles/'

# Hansen gain tiles (2001-2012)
pattern_gain = 'Hansen_GFC2015_gain'
gain_dir = 's3://gfw2-data/forest_change/tree_cover_gain/gaindata_2012/'

# Tree cover density 2000 tiles
pattern_tcd = 'Hansen_GFC2014_treecover2000'
tcd_dir = 's3://gfw2-data/forest_cover/2000_treecover/'

# Intact forest landscape 2000 tiles
pattern_ifl = 'res_ifl_2000'
ifl_dir = 's3://gfw2-data/climate/carbon_model/other_emissions_inputs/ifl_2000/'

# Processed FAO ecozone shapefile
cont_ecozone_shp = 'fao_ecozones_fra_2000_continents_assigned_dissolved_FINAL_20180906.zip'

# Directory and names for the continent-ecozone tiles, raw and processed
pattern_cont_eco_raw = 'fao_ecozones_continents_raw'
pattern_cont_eco_processed = 'fao_ecozones_continents_processed'
cont_eco_zip = 's3://gfw2-data/climate/carbon_model/fao_ecozones/fao_ecozones_fra_2000_continents_assigned_dissolved_FINAL_20180906.zip'
cont_eco_raw_dir = 's3://gfw2-data/climate/carbon_model/fao_ecozones/ecozone_continent/20181002/raw/'
cont_eco_dir = 's3://gfw2-data/climate/carbon_model/fao_ecozones/ecozone_continent/20181002/processed/'

# Number of gain years for non-mangrove natural forests
pattern_gain_year_count_natrl_forest = 'gain_year_count_natural_forest'
gain_year_count_natrl_forest_dir = 's3://gfw2-data/climate/carbon_model/gain_year_count_natural_forest/20181031/'

# Number of gain years for mangroves
pattern_gain_year_count_mangrove = 'gain_year_count_mangrove'
gain_year_count_mangrove_dir = 's3://gfw2-data/climate/carbon_model/gain_year_count_mangrove/20181031/'

# Forest age category tiles
pattern_age_cat_natrl_forest = 'forest_age_category_natural_forest'
age_cat_natrl_forest_dir = 's3://gfw2-data/climate/carbon_model/forest_age_category_natural_forest/20180921/'


# Annual aboveground biomass gain rate for non-mangrove natural forests
pattern_annual_gain_AGB_natrl_forest = 'annual_rate_AGB_t_ha_natural_forest'
annual_gain_AGB_natrl_forest_dir = 's3://gfw2-data/climate/carbon_model/annual_gain_rate_AGB_natural_forest/20181101/'

# Annual aboveground biomass gain rate for mangroves
pattern_annual_gain_AGB_mangrove = 'annual_rate_AGB_t_ha_mangrove'
annual_gain_AGB_mangrove_dir = 's3://gfw2-data/climate/carbon_model/annual_gain_rate_AGB_mangrove/20181101/'

# Annual belowground biomass gain rate for non-mangrove natural forests
pattern_annual_gain_BGB_natrl_forest = 'annual_rate_BGB_t_ha_natural_forest'
annual_gain_BGB_natrl_forest_dir = 's3://gfw2-data/climate/carbon_model/annual_gain_rate_BGB_natural_forest/20181101/'

# Annual belowground biomass gain rate for mangroves
pattern_annual_gain_BGB_mangrove = 'annual_rate_BGB_t_ha_mangrove'
annual_gain_BGB_mangrove_dir = 's3://gfw2-data/climate/carbon_model/annual_gain_rate_BGB_mangrove/20181101/'


# Cumulative aboveground gain for natural forests
pattern_cumul_gain_AGC_natrl_forest = 'cumul_gain_AGC_t_ha_natural_forest_2001_15'
cumul_gain_AGC_natrl_forest_dir = 's3://gfw2-data/climate/carbon_model/cumulative_gain_AGC_natural_forest/20181101/'

# Cumulative aboveground gain for mangroves
pattern_cumul_gain_AGC_AGC_mangrove = 'cumul_gain_AGC_t_ha_mangrove_2001_15'
cumul_gain_AGC_mangrove_dir = 's3://gfw2-data/climate/carbon_model/cumulative_gain_AGC_mangrove/20181101/'

# Cumulative aboveground gain for natural forests
pattern_cumul_gain_BGC_natrl_forest = 'cumul_gain_BGC_t_ha_natural_forest_2001_15'
cumul_gain_BGC_natrl_forest_dir = 's3://gfw2-data/climate/carbon_model/cumulative_gain_BGC_natural_forest/20181101/'

# Cumulative aboveground gain for mangroves
pattern_cumul_gain_BGC_mangrove = 'cumul_gain_BGC_t_ha_mangrove_2001_15'
cumul_gain_BGC_mangrove_dir = 's3://gfw2-data/climate/carbon_model/cumulative_gain_BGC_mangrove/20181101/'


# Annual aboveground gain rate for all forest types
pattern_annual_gain_combo = 'annual_gain_rate_t_C_ha_all_forest_types'
annual_gain_combo_dir = 's3://gfw2-data/climate/carbon_model/annual_AGC_gain_rate_all_forest_types/20181101/'

# Cumulative gain for all forest types
pattern_cumul_gain_combo = 'aboveground_C_gain_t_C_ha_all_forest_types_2001_15'
cumul_gain_combo_dir = 's3://gfw2-data/climate/carbon_model/cumulative_gain_all_forest_types/20181101/'

def s3_folder_download(source, dest):
    cmd = ['aws', 's3', 'cp', source, dest, '--recursive']
    subprocess.check_call(cmd)

def s3_file_download(source, dest):
    cmd = ['aws', 's3', 'cp', source, dest]
    subprocess.check_call(cmd)

# Lists the tiles in a folder in s3
def tile_list(source):

    ## For an s3 folder in a bucket using AWSCLI
    # Captures the list of the files in the folder
    out = subprocess.Popen(['aws', 's3', 'ls', source], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()

    # Writes the output string to a text file for easier interpretation
    biomass_tiles = open("biomass_tiles.txt", "w")
    biomass_tiles.write(stdout)
    biomass_tiles.close()

    file_list = []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open("biomass_tiles.txt", 'r') as tile:
        for line in tile:
            num = len(line.strip('\n').split(" "))
            tile_name = line.strip('\n').split(" ")[num - 1]

            # Only tifs will be in the tile list
            if '.tif' in tile_name:

                # For stripping down standard tree biomass tiles to the tile id
                if '_biomass.tif' in tile_name:

                    tile_short_name = tile_name.replace('_biomass.tif', '')
                    file_list.append(tile_short_name)

                # For stripping down mangrove biomass tiles to the tile id
                if pattern_mangrove_biomass in tile_name:

                    tile_short_name = tile_name.replace('{}_'.format(pattern_mangrove_biomass), '')
                    tile_short_name = tile_short_name.replace('.tif', '')
                    file_list.append(tile_short_name)
                    file_list = file_list[0:]

    return file_list

# Gets the bounding coordinates of a tile
def coords(tile_id):
    NS = tile_id.split("_")[0][-1:]
    EW = tile_id.split("_")[1][-1:]

    if NS == 'S':
        ymax =-1*int(tile_id.split("_")[0][:2])
    else:
        ymax = int(str(tile_id.split("_")[0][:2]))

    if EW == 'W':
        xmin = -1*int(str(tile_id.split("_")[1][:3]))
    else:
        xmin = int(str(tile_id.split("_")[1][:3]))


    ymin = str(int(ymax) - 10)
    xmax = str(int(xmin) + 10)

    return ymax, xmin, ymin, xmax

# Rasterizes the shapefile within the bounding coordinates of a tile
def rasterize(in_shape, out_tif, xmin, ymin, xmax, ymax, tr=None, ot=None, gainEcoCon=None, anodata=None):
    cmd = ['gdal_rasterize', '-co', 'COMPRESS=LZW',

           # Input raster is ingested as 1024x1024 pixel tiles (rather than the default of 1 pixel wide strips
           '-co', 'TILED=YES', '-co', 'BLOCKXSIZE=1024', '-co', 'BLOCKYSIZE=1024',
           '-te', str(xmin), str(ymin), str(xmax), str(ymax),
           '-tr', tr, tr, '-ot', ot, '-a', gainEcoCon, '-a_nodata',
           anodata, in_shape, '{}.tif'.format(out_tif)]

    subprocess.check_call(cmd)

    return out_tif

# Uploads tile to specified location
def upload_final(pattern, upload_dir, tile_id):

    file = '{}_{}.tif'.format(pattern, tile_id)

    print "Uploading {}".format(file)
    cmd = ['aws', 's3', 'cp', file, upload_dir]

    try:
        subprocess.check_call(cmd)
    except:
        print "Error uploading output tile"



##### Not currently using the below functions


def wgetloss(tile_id):
    print "download hansen loss tile"
    cmd = ['wget', r'http://glad.geog.umd.edu/Potapov/GFW_2015/tiles/{}.tif'.format(tile_id)]

    subprocess.check_call(cmd)


def wget2015data(tile_id, filetype):

    outfile = '{0}_{1}_h.tif'.format(tile_id, filetype)

    website = 'https://storage.googleapis.com/earthenginepartners-hansen/GFC-2015-v1.3/Hansen_GFC-2015-v1.3_{0}_{1}.tif'.format(filetype, tile_id)
    cmd = ['wget', website, '-O', outfile]
    print cmd

    subprocess.check_call(cmd)

    return outfile


def rasterize_shapefile(xmin, ymax, xmax, ymin, shapefile, output_tif, attribute_field):
    layer = shapefile.replace(".shp", "")
    # attribute_field = 'old_100'
    cmd= ['gdal_rasterize', '-te', str(xmin), str(ymin), str(xmax), str(ymax), '-a', attribute_field, '-co', 'COMPRESS=LZW', '-tr', '.00025', '.00025', '-tap', '-a_nodata', '0', '-l', layer, shapefile, output_tif]

    subprocess.check_call(cmd)

    return output_tif


def resample_00025(input_tif, resampled_tif):
    # resample to .00025
    cmd = ['gdal_translate', input_tif, resampled_tif, '-tr', '.00025', '.00025', '-co', 'COMPRESS=LZW']
    subprocess.check_call(cmd)
