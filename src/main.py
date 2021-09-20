import os
from datetime import datetime
from util.logging import setup_log_level
from util.parser import setup_command_line
from features.P0_create_package_catalog import create_package_catalog
from features.P1_construct_initial_dataframe import processCatalogCSV


PATH = "lts/"  # directory of packages
parser = setup_command_line()
args = parser.parse_args()
logging = setup_log_level(args)

date_now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
csv_file = create_package_catalog(PATH, date_now)
initial_df = processCatalogCSV(os.path.join(os.path.dirname(__file__), csv_file), date_now)
