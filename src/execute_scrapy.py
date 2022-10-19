from subprocess import call
import os
import argparse

parser = argparse.ArgumentParser(
    description='Generate a CSV file with package catalog')
parser.add_argument(
    "--revised", help="Set the PATH  to make and save the DataFrames with revised Cabals", action='store_true', default=False)

args = parser.parse_args()
isRevisedVersion = '--revised' if args.revised else '' 

path = os.path.join(os.path.dirname(__file__),"..//src//scrapy//scrapy_lts.py")
print(path)
os.chdir(os.getcwd()+'\\scrapy')
print(os.getcwd())
if(isRevisedVersion != ''):
    call(["python",path,isRevisedVersion])
else:
    call(["python",path])