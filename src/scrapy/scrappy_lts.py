from subprocess import call
import os
import argparse


parser = argparse.ArgumentParser(
    description='Generate a CSV file with package catalog')
parser.add_argument(
    "--revised", help="Set the PATH  to make and save the DataFrames with revised Cabals", action='store_true', default=False)
    
args = parser.parse_args()
isRevisedVersion = args.revised
#lts_list = ['0-7']
lts_list=['0-7', '2-22', '3-22', '6-35', '7-24', '9-21', '11-22', '12-14', '12-26', 
'13-11','13-19', '14-27', '15-3', '16-11', '16-31', '17-2', '18-6', '18-8', '18-28', '19-11']


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