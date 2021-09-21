import os
from datetime import datetime
import pandas as pd
from util.logging import setup_log_level
from util.parser import setup_command_line
from features.P0_create_package_catalog import create_package_catalog
from features.P1_construct_initial_dataframe import process_catalog_csv
from features.P2_construct_dataframe_with_paths import construct_df_with_paths


PATH = "C:/Users/nicol/Desktop/lts/lts-test"  # directory of packages
parser = setup_command_line()
args = parser.parse_args()
logging = setup_log_level(args)

date_now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
csv_file = create_package_catalog(PATH, date_now, logging)
initial_df = process_catalog_csv(os.path.join(
    os.path.dirname(__file__), csv_file), logging)

df_with_paths = construct_df_with_paths(PATH, initial_df, logging)
