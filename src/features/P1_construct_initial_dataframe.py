#!/usr/bin/env python

from __future__ import print_function
from datetime import datetime

import os, logging, argparse
import subprocess
import csv as csv
import pandas as pd
import copy

####################################################################################
## We parse the package-catalog CSV file to construct the initial dataframe
## The dataframe is indexed by package name, and holds the following columns:
##     - version
##     - stability
##     - cabal-file: path to the cabal file that generated this data
##     - deps: list of package dependencies
##     - provided-modules: list of module names, the modules exposed by the package
##     - src-dirs: directories in the package that contain actual source code
##     - mtl-direct: indicates whether the package directly imports the mtl. 1 it does, 0 it doesn't
## 
def processCatalogCSV(csvFilename, nowStr, logger):
    logger.info("Constructing initial dataframe")
    data = []
    for row in csv.reader(open(csvFilename), delimiter=";"):
        data.append(row)

    pkgidx = 0
    veridx = 1
    staidx = 2
    cblidx = 3
    catidx = 4
    depidx = 5
    modidx = 6
    srcidx = 7    
    mainidx = 8

    for row in data:
        row[staidx]  = row[staidx].split(",")[0].strip().lower()
        row[catidx]  = filter(None, map(lambda x: x.strip().lower(), row[catidx].split(",")))
        row[depidx]  = filter(None, map(lambda x: x.strip().lower(), row[depidx].split(",")))
        row[modidx]  = filter(None, row[modidx].split(","))
        row[srcidx]  = filter(None, row[srcidx].split(","))
        row[mainidx] = filter(None, row[mainidx].split(","))
    
    data = map(list, zip(*data))    
    Headers = ["%s-%s" % (x[0], x[1]) for x in zip(data[0], data[1])]    

    # Add empty list for mtl-direct column
    data.append([])
    mtlidx = len(data) - 1

    ## Define bit-vector of direct mtl
    for i in range(len(data[0])):
        if "mtl" in data[depidx][i]:
            data[mtlidx].append(1)
        else:
            data[mtlidx].append(0)

    df = pd.DataFrame(data, columns=Headers).transpose()
    df.columns = ['package', 'version', 'stability', 'cabal-file', 'categories', 'deps', 'provided-modules', 'src-dirs',  'main-modules', 'mtl-direct']
    df.sort_index(inplace = True)

    df.to_pickle("package-dataframe-%s.df" % nowStr)
    logger.info("Finishing work at %s" % str(datetime.now()))


########################## MAIN ##########################

parser = argparse.ArgumentParser()
parser.add_argument("catalog", help="Path to CSV file containing the package catalog")
parser.add_argument("-v", "--verbose", help="Set log level to DEBUG to increase output verbosity", action="store_true")
parser.add_argument("-q", "--quiet", help="Set log level to ERROR to decrease output verbosity", action="store_true")

args = parser.parse_args()
if args.verbose:
   logging.basicConfig(level=logging.DEBUG)
elif args.quiet:
   logging.basicConfig(level=logging.ERROR)
else:
   logging.basicConfig(level=logging.INFO)

csvFilename = args.catalog
nowStr = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
processCatalogCSV(csvFilename, nowStr, logging)