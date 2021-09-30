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
    dependencies_version = list(
        map(lambda x: tuple(x.split(' ', 1)), data[5].split(',')))
    return {
        'package': data[0],
        'version': data[1],
        'stability': list(map(lambda x: x.strip().lower(), data[2].replace('"', "").split(','))),
        'cabal-file': data[4],
        'categories': list(map(lambda x: x.strip().lower(), data[3].replace('"', "").split(','))),
        'deps': list(map(lambda x: x[0], dependencies_version)) if len(data[5]) != 0 else [],
        'provided-modules': data[6].split(','),
        'src-dirs': data[7].split(','),
        'main-modules': data[8].split(','),
        'mtl-direct': depends_of_mtl(data),
        'version-range-deps': dependencies_version if len(data[5]) != 0 else []
    }


def process_catalog_csv(csvFilename, logger, lts):
    logger.info("Constructing initial dataframe")
    data = []
    for row in csv.reader(open(csvFilename), delimiter=";"):
        data.append(row)

    metadata_list = []
    meta_index = []
    for row in data:
        name_index = row[0]+'-'+row[1]
        meta_index.append(name_index)
        metadata = build_metadata(row)
        metadata_list.append(metadata)

    df = pd.DataFrame(metadata_list, index=meta_index, columns=['package', 'version', 'stability', 'cabal-file', 'categories',
                      'deps', 'provided-modules', 'src-dirs',  'main-modules', 'mtl-direct', 'version-range-deps'])
    df.sort_index(inplace=True)
    df_path = "C:/Users/nicol/Documents/GitHub/stackage-evolution/data/test/%s/%s.df" % (
        lts, lts)
    df.to_pickle(df_path)
    logger.debug(df[['package', 'main-modules']])

    logger.info("Finishing work at %s" % str(datetime.now()))

    return df_path
