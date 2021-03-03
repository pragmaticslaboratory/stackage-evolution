#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from datetime import datetime

import argparse, logging, sys, copy, os
import pandas as pd
import numpy as np
import scipy.stats as ss


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i : i + n]


####################################################################################
def generateDataframeByCategory(df):
    """Takes a dataframe where a package has 1+ categories, and generates a new
    dataframe with unique package-category combinations, hence reflecting
    the multiplicity of categories by package
    """

    logging.info("Creating dataframe split by category")
    multicat_criteria = df["categories"].map(lambda x: len(x) > 1)

    catdf = df.copy()
    for idx in catdf.index:
        if len(catdf.loc[idx]["categories"]) == 1:
            theCat = catdf.loc[idx]["categories"][0]
            catdf.set_value(idx, "categories", theCat)

    additionalrows = []

    for idx in catdf[multicat_criteria].index:
        currentRow = copy.deepcopy(df.loc[idx])
        for cat in currentRow["categories"]:
            newRow = copy.deepcopy(currentRow)
            newRow["categories"] = cat
            additionalrows.append(newRow)

    catdf = catdf.drop(catdf[multicat_criteria].index)
    catdf = catdf.append(additionalrows)
    catdf = catdf.sort_index()
    catdf.columns = [
        "category" if x == "categories" else x for x in catdf.columns.tolist()
    ]
    catdf["category"] = catdf["category"].apply(str)
    catdf.to_pickle("%s-with-monad-usage-by-category.df" % args.df.replace(".df", ""))
    logging.info("Done creating dataframe split by category")


####################################################################################
def generateMonadUsageDataframe():
    """Takes a dataframe with the information of imported modules, and yields
    a new dataframe with the usage information of each monad in the mtl_modules list.
    """

    df = pd.read_pickle(args.df)

    listToProcess = df.index.tolist()
    pkgTotal = len(listToProcess)
    nthreads = 4
    step = max(1, len(listToProcess) / nthreads)

    packagesMonadUsage = {}

    pkgNum = 1
    logging.info("Starting work at %s" % str(datetime.now()))

    for chunk in chunks(listToProcess, step):
        flatPkgImportedModules = [
            (idx, df.loc[idx]["imported-modules"]) for idx in chunk
        ]
        for pkg, imods in flatPkgImportedModules:
            pkgMonadUsage = {}
            for mtl_mod in mtl_modules:
                if mtl_mod in imods:
                    pkgMonadUsage[mtl_mod] = 1
                else:
                    pkgMonadUsage[mtl_mod] = 0

            for other_mod in other_modules:
                if other_mod in imods:
                    pkgMonadUsage[other_mod] = 1
                else:
                    pkgMonadUsage[other_mod] = 0

            packagesMonadUsage[pkg] = pkgMonadUsage

    #####################################################################
    logging.info("Computing monad usage")

    ## Add columns to dataframe

    moduleMonadUsageSeries = {}

    ### For MTL modules ##########################################################
    for mtl_mod in mtl_modules:
        moduleMonadUsageSeries[mtl_mod] = []
        for idx in listToProcess:
            moduleMonadUsageSeries[mtl_mod].append(packagesMonadUsage[idx][mtl_mod])

    for mtl_mod in mtl_modules:
        df[mtl_mod] = pd.Series(moduleMonadUsageSeries[mtl_mod], index=df.index)

    ### For other non-MTL modules ##########################################################
    for other_mod in other_modules:
        moduleMonadUsageSeries[other_mod] = []
        for idx in listToProcess:
            moduleMonadUsageSeries[other_mod].append(packagesMonadUsage[idx][other_mod])

    for other_mod in other_modules:
        df[other_mod] = pd.Series(moduleMonadUsageSeries[other_mod], index=df.index)

    df.to_pickle(full_df_path)
    generateDataframeByCategory(df)
    logging.info("Finishing work at %s" % str(datetime.now()))


################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("df", help="Dataframe file with package imports")
parser.add_argument(
    "-v",
    "--verbose",
    help="Set log level to DEBUG to increase output verbosity",
    action="store_true",
)
parser.add_argument(
    "-q",
    "--quiet",
    help="Set log level to ERROR to decrease output verbosity",
    action="store_true",
)

args = parser.parse_args()
if args.verbose:
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
elif args.quiet:
    logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
else:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

##################################################################
## These are all the modules provided by the mtl library
## which will be matched against the imports of every package.
##

## https://wiki.haskell.org/All_About_Monads
##

mtl_modules = [
    "Control.Monad.Cont",
    "Control.Monad.Cont.Class",
    "Control.Monad.Error",
    "Control.Monad.Error.Class",
    "Control.Monad.Except",
    "Control.Monad.Identity",
    "Control.Monad.List",
    "Control.Monad.RWS",
    "Control.Monad.RWS.Class",
    "Control.Monad.RWS.Lazy",
    "Control.Monad.RWS.Strict",
    "Control.Monad.Reader",
    "Control.Monad.Reader.Class",
    "Control.Monad.State",
    "Control.Monad.State.Class",
    "Control.Monad.State.Lazy",
    "Control.Monad.State.Strict",
    "Control.Monad.Trans",
    "Control.Monad.Writer",
    "Control.Monad.Writer.Class",
    "Control.Monad.Writer.Lazy",
    "Control.Monad.Writer.Strict",
    "Control.Monad.Trans",
    "Control.Monad.Trans.Class",
]

other_modules = ["Control.Monad", "System.IO"]


####################################################################################
## Do not generate full dataframe if it already exists
full_df_path = "%s-with-monad-usage.df" % args.df.replace(".df", "")
if not os.path.isfile(full_df_path):
    generateMonadUsageDataframe()
else:
    logging.info("Not creating file %s because it already exists" % full_df_path)