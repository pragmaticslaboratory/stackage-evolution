import errno
import os
import glob
import pandas as pd
from datetime import datetime
from util.logging import setup_log_level
from util.parser import setup_command_line
from features.P0_create_package_catalog import create_package_catalog,create_package_catalog_revision
from features.P1_construct_initial_dataframe import process_catalog_csv
from features.P2_construct_dataframe_with_paths import construct_df_with_paths
from features.P3_construct_dataframe_with_imports import construct_df_with_imports
from features.P4_construct_dataframe_with_mtl_usage import generate_monad_usage_dataframe
#from features.P5_fix_paths import fix_paths
from features.P6_get_method_calls import get_methods_calls

data = pd.read_csv("lts_list.csv")
lts_list = data.columns

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
        path = os.path.join(os.path.dirname(__file__),"../lts_downloaded/tar_package/lts-%s"% lts_version)
        directory_path = os.path.join(os.path.dirname(__file__),"../data/dfs/lts-%s"% lts_version)
    else:
        path = os.path.join(os.path.dirname(__file__),"../lts_downloaded/revised_cabal/lts-%s"% lts_version)   
        directory_path = os.path.join(os.path.dirname(__file__),"../data/dfs_revissed/lts-%s"% lts_version)
    #Change the path to work with the wsl directions
    if(isWsl):
        path = wsl + path[3:]
        directory_path = wsl + directory_path[3:]

    try:
        os.mkdir(directory_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    date_now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    print("*-------------------------Starting with %s-------------------------*" % lts_version)
    if(not isRevisedVersion):
        csv_file = create_package_catalog(path,directory_path, date_now, logging)
    else:
        csv_file = create_package_catalog_revision(path,directory_path, date_now, logging)
    initial_df = process_catalog_csv(os.path.join(os.path.dirname(__file__), csv_file), logging, directory_path,lts_version)
    df_with_paths = construct_df_with_paths(path, initial_df, logging)
    df_with_imports = construct_df_with_imports(df_with_paths, logging)
    df_with_monads_categories = generate_monad_usage_dataframe(directory_path+"/lts-%s-with-paths-with-imports.df" % lts_version, logging, directory_path, lts_version)
    # df_fix_paths = fix_paths(PATH, df_with_imports, logging, lts) use in case of change paths
    # df_with_methods = get_methods_calls(df_with_imports, logging)
