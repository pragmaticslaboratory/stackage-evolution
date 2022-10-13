from subprocess import call
import os
import argparse
import pandas as pd

parser = argparse.ArgumentParser(
    description='Generate a CSV file with package catalog')
parser.add_argument(
    "--revised", help="Set the PATH  to make and save the DataFrames with revised Cabals", action='store_true', default=False)
    
args = parser.parse_args()
isRevisedVersion = args.revised
#lts_list = ['0-7']

data = pd.read_csv("../util/lts_list.csv")
lts_list = data.columns
for lts in lts_list:
    if(isRevisedVersion):
        path = os.path.join(os.path.dirname(__file__),"..\\..\\lts_downloaded\\revised_cabal")
    else:
        path = os.path.join(os.path.dirname(__file__),"..\\..\\lts_downloaded\\tar_package")
    lts_dots = lts.replace("-",".")
    path = path+"/lts-"+lts
    comand = 'scrapy crawl stackage -a LTS="%s" -s FILES_STORE="%s" -s REVISSED="%s"' % (lts_dots, path, isRevisedVersion)
    print(comand)
    call(comand)