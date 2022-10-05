import errno
import os
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
lts_list = ['0-7', '2-22', '3-22', '6-35', '7-24', '9-21', '11-22', '12-14', '12-26', '13-11',
            '13-19', '14-27', '15-3', '16-11', '16-31', '17-2', '18-6', '18-8', '18-28', '19-11']

windows = "C:/"
wsl = "/mnt/c/"
for lts_version in lts_list:
    PATH = windows+"Users/nicol/Desktop/lts/lts-%s" % lts_version # directory of packages
    PATHREVISION = windows+"Users/nicol/Desktop/lts/Test/lts-%s" % lts_version  # directory of revision cabal
    lts = PATH.split('/')[-1]
    parser = setup_command_line()
    args = parser.parse_args()
    logging = setup_log_level(args)

    directory_path = windows+"Users/nicol/Documents/GitHub/data/%s" % lts
    try:
        os.mkdir(directory_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    date_now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    #csv_file = create_package_catalog_revision(PATHREVISION, date_now, logging, lts)
    '''csv_file = create_package_catalog(PATH, date_now, logging, lts) #use only for use the path of Tar to extract the cabal package
    initial_df = process_catalog_csv(os.path.join(
        os.path.dirname(__file__), csv_file), logging, lts)
    df_with_paths = construct_df_with_paths(PATH, initial_df, logging)
    df_with_imports = construct_df_with_imports(df_with_paths, logging)'''
    df_with_monads_categories = generate_monad_usage_dataframe(directory_path+"/lts-%s-with-paths-with-imports.df" % lts_version, logging, lts)
    # df_fix_paths = fix_paths(PATH, df_with_imports, logging, lts) use in case of change paths
    # df_with_methods = get_methods_calls(df_with_imports, logging)
