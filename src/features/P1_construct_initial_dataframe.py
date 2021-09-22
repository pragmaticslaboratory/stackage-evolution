#!/usr/bin/env python

from __future__ import print_function
from datetime import datetime

import csv as csv
import pandas as pd
####################################################################################
# We parse the package-catalog CSV file to construct the initial dataframe
# The dataframe is indexed by package name, and holds the following columns:
# - version
# - stability
# - cabal-file: path to the cabal file that generated this data
# - deps: list of package dependencies
# - provided-modules: list of module names, the modules exposed by the package
# - src-dirs: directories in the package that contain actual source code
# - mtl-direct: indicates whether the package directly imports the mtl. 1 it does, 0 it doesn't
##


def depends_of_mtl(data):
    dependencies = data[5].split(',')
    return 1 if 'mtl' in dependencies else 0


def build_metadata(data):
    return {
        'package': data[0],
        'version': data[1],
        'stability': list(map(lambda x: x.strip().lower(), data[2].replace('"', "").split(','))),
        'cabal-file': data[4],
        'categories': list(map(lambda x: x.strip().lower(), data[3].replace('"', "").split(','))),
        'deps': data[5].split(','),
        'provided-modules': data[6],
        'src-dirs': data[7],
        'main-modules': data[8],
        'mtl-direct': depends_of_mtl(data)
    }


def process_catalog_csv(csvFilename, logger):
    logger.info("Constructing initial dataframe")
    data = []
    for row in csv.reader(open(csvFilename), delimiter=";"):
        data.append(row)

    metadata_list = []
    for row in data:
        metadata = build_metadata(row)
        metadata_list.append(metadata)

    df = pd.DataFrame(metadata_list, columns=['package', 'version', 'stability', 'cabal-file', 'categories',
                                              'deps', 'provided-modules', 'src-dirs',  'main-modules', 'mtl-direct'])
    df.sort_index(inplace=True)
    df.to_pickle("./package-dataframe.df")
    logger.debug(df[['package', 'main-modules']])

    logger.info("Finishing work at %s" % str(datetime.now()))

    return "./package-dataframe.df"
