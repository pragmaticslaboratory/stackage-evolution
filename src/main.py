import os
from datetime import datetime
from util.logging import setup_log_level
from util.parser import setup_command_line
from features.P0_create_package_catalog import create_package_catalog
from features.P1_construct_initial_dataframe import process_catalog_csv
from features.P2_construct_dataframe_with_paths import construct_df_with_paths
from features.P3_construct_dataframe_with_imports import construct_df_with_imports
from features.P4_construct_dataframe_with_mtl_usage import generate_monad_usage_dataframe
from features.P5_fix_paths import fix_paths
from features.P6_get_method_calls import get_methods_calls

PATH = "C:/Users/nicol/Desktop/lts/lts-test"  # directory of packages
lts = PATH.split('/')[-1]
parser = setup_command_line()
args = parser.parse_args()
logging = setup_log_level(args)

date_now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
csv_file = create_package_catalog(PATH, date_now, logging)
initial_df = process_catalog_csv(os.path.join(
    os.path.dirname(__file__), csv_file), logging)
df_with_paths = construct_df_with_paths(PATH, initial_df, logging)
df_with_imports = construct_df_with_imports(df_with_paths, logging)
df_with_monads_categories = generate_monad_usage_dataframe(
    df_with_imports, logging)
df_fix_paths = fix_paths(PATH, df_with_imports, logging, lts)
df_with_methods = get_methods_calls(df_fix_paths, logging)
