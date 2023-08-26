import traceback #pleger (to catch error trace)

import errno
import os
import pandas as pd
from datetime import datetime
from util.logging import setup_log_level
from util.parser import setup_command_line
from util.generate_parse_exe import generate_parse_exe
from features.P0_create_package_catalog import create_package_catalog,create_package_catalog_revision
from features.P1_construct_initial_dataframe import process_catalog_csv
from features.P2_construct_dataframe_with_paths import construct_df_with_paths
from features.P3_construct_dataframe_with_imports import construct_df_with_imports
from features.P4_construct_dataframe_with_mtl_usage import generate_monad_usage_dataframe
#from features.P5_fix_paths import fix_paths
from features.P6_get_method_calls import get_methods_calls

data = pd.read_csv("lts_list.csv")
lts_list = data.columns
#0-7,2-22,3-22,6-35,7-24,9-21,11-22,12-14,12-26,13-11,13-19,14-27,15-3,16-11,16-31,17-2,18-6,18-8,18-28,19-11
wsl = "/mnt/c/"
#Set the arguments values
parser = setup_command_line()
args = parser.parse_args()
isWsl = args.wsl
isRevisedVersion = args.revised
logging = setup_log_level(args)

FOLDERPATH =  os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]

generate_parse_exe(FOLDERPATH)

#change the directory to generate_dfs path
os.chdir(FOLDERPATH+'/src')
for lts_version in lts_list:
    #Set the path where are located the downloaded package, and the directory path where the DataFrames will be save
    if(not isRevisedVersion):
        path = FOLDERPATH + "/lts_downloaded/tar_package/lts-%s"% lts_version
        directory_path = FOLDERPATH+ "/data/dfs/lts-%s"% lts_version
    else:
        path = FOLDERPATH + "/lts_downloaded/revised_cabal/lts-%s"% lts_version 
        directory_path = FOLDERPATH+"/data/dfs_revised/lts-%s"% lts_version
    #Change the path to work with the wsl directions
    if(isWsl):
        path = wsl + path[3:]
        directory_path = wsl + directory_path[3:]

    try:
        print(directory_path)
        os.mkdir(directory_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    date_now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    print("*-------------------------Starting with %s-------------------------*" % lts_version)
    try:
        dir = os.listdir(path)
        if len(dir) == 0:
            print("Empty directory")
        else:
            if(not isRevisedVersion):
                csv_file = create_package_catalog(path,directory_path, date_now, logging)
            else:
                csv_file = create_package_catalog_revision(path,directory_path, date_now, logging)
            lts_version = "lts-"+lts_version
            print("*-------------------------Starting initial df -------------------------*")
            initial_df = process_catalog_csv(os.path.join(os.path.dirname(__file__), csv_file), logging, directory_path,lts_version)
            print("*-------------------------Starting with paths-------------------------*")
            df_with_paths = construct_df_with_paths(path, initial_df, logging)
            print("*-------------------------Starting with imports-------------------------*")
            df_with_imports = construct_df_with_imports(df_with_paths, logging)
            print("*-------------------------Starting with category monad-------------------------*")
            df_with_monads_categories = generate_monad_usage_dataframe(directory_path+"/%s-with-paths-with-imports.df" % lts_version, logging, directory_path, lts_version)
            # df_fix_paths = fix_paths(PATH, df_with_imports, logging, lts) use in case of change paths
            # df_with_methods = get_methods_calls(df_with_imports, logging)
    except Exception as e:
        print(e)
        traceback.print_exc() #pleger error trace
        print("The folder lts-%s doesn't exist" % lts_version)
