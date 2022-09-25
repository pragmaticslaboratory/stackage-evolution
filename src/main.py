import errno
import os
import glob
from datetime import datetime
from argparse import ArgumentParser
from util.logging import setup_log_level
from util.parser import setup_command_line
from features.P0_create_package_catalog import create_package_catalog,create_package_catalog_revision
from features.P1_construct_initial_dataframe import process_catalog_csv
from features.P2_construct_dataframe_with_paths import construct_df_with_paths
from features.P3_construct_dataframe_with_imports import construct_df_with_imports
from features.P4_construct_dataframe_with_mtl_usage import generate_monad_usage_dataframe
#from features.P5_fix_paths import fix_paths
from features.P6_get_method_calls import get_methods_calls

PATH = os.path.join(os.path.dirname(__file__),"../lts_downloaded/Revised_Cabal")
list_url = glob.glob(f"{PATH}/*")
lts_list = [lts.split('lts-')[1].replace('-','.') for lts in list_url]
lts_list = sorted(lts_list, key=lambda x: float(x))
lts_list = [lts.replace('.','-') for lts in lts_list]
lts_list.remove('18-28')
lts_list.insert(18,'18-28')

wsl = "/mnt/c/"
#Set the arguments values
parser = setup_command_line()
args = parser.parse_args()
isWsl = args.wsl
isRevisedVersion = args.revised
logging = setup_log_level(args)

for lts_version in lts_list:
    #Set the path where are located the downloaded package, and the directory path where the DataFrames will be save
    if(not isRevisedVersion):
        PATH = os.path.join(os.path.dirname(__file__),"../lts_downloaded/Tar_Package/lts-%s"% lts_version)
        directory_path = os.path.join(os.path.dirname(__file__),"../data/Dfs/lts-%s"% lts_version)
    else:
        PATH = os.path.join(os.path.dirname(__file__),"../lts_downloaded/Revised_Cabal/lts-%s"% lts_version)   
        directory_path = os.path.join(os.path.dirname(__file__),"../data/Dfs_Revissed/lts-%s"% lts_version)
    #Change the path to work with the wsl directions
    if(isWsl):
        PATH = wsl + PATH[3:]
        directory_path = wsl + directory_path[3:]

    try:
        os.mkdir(directory_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    date_now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    if(not isRevisedVersion):
        csv_file = create_package_catalog(PATH,directory_path, date_now, logging)
    else:
        csv_file = create_package_catalog_revision(PATH,directory_path, date_now, logging)
    initial_df = process_catalog_csv(os.path.join(
        os.path.dirname(__file__), csv_file), logging, directory_path,lts_version)
    df_with_paths = construct_df_with_paths(PATH, initial_df, logging)
    df_with_imports = construct_df_with_imports(df_with_paths, logging)
    df_with_monads_categories = generate_monad_usage_dataframe(directory_path+"/lts-%s-with-paths-with-imports.df" % lts_version, logging, directory_path, lts_version)
    # df_fix_paths = fix_paths(PATH, df_with_imports, logging, lts) use in case of change paths
    # df_with_methods = get_methods_calls(df_with_imports, logging)
