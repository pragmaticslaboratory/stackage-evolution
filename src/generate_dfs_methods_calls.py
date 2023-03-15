import pandas as pd
import os
from datetime import datetime
from features.P6_get_method_calls import get_methods_calls
from util.logging import setup_log_level
from util.parser import setup_command_line

parser = setup_command_line()
args = parser.parse_args()
logging = setup_log_level(args)

FOLDERPATH =  os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
data = pd.read_csv("lts_list.csv")
lts_list = data.columns

for lts_version in lts_list:
    date_now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    df_path = FOLDERPATH + "/data/dfs/lts-%s/lts-%s.df" % (lts_version,lts_version)

    print("*-------------------------Starting with %s-------------------------*" % lts_version)
    df_with_methods = get_methods_calls(df_path, logging)