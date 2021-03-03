#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from datetime import datetime

import os, argparse, logging, sys, pickle
import pandas as pd
import subprocess
import re

parser = argparse.ArgumentParser()
parser.add_argument(
    "df", help="Dataframe file with package catalog description that has module paths"
)
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

df_paths = pd.read_pickle(args.df)

###########################################################################################
## This script processes each package in the dataframe, parsing all their provided modules
## to determine all imported modules in each package. The parsing and extraction is
## performed by the PackageImport.hs program
##

listToProcess = df_paths.index.tolist()
pkgTotal = len(listToProcess)

packageImports = {}
pickle_file_pattern = "./pickles/pkg_imports_%s.pickle"

pkgNum = 1
logging.info("Starting work at %s" % str(datetime.now()))
for idx in listToProcess:
    logging.info("[%s] Processing" % idx)

    # to do: change the path by OS

    pkg, mods, mains, cabal_file = (
        idx,
        map(lambda x: x[1], df_paths.loc[idx]["provided-modules-found"]),
        map(lambda x: x, df_paths.loc[idx]["main-modules-found"]),
        df_paths.loc[idx]["cabal-file"],
    )
    package_paths = [cabal_file] + mods + mains
    paths_for_input = "\n".join(package_paths)

    logging.debug(
        "[%s] Input paths (%d):\n%s" % (idx, len(package_paths), paths_for_input)
    )

    pickle_file = str(pickle_file_pattern % idx.replace(".", "-"))
    if not os.path.isfile(pickle_file):
        try:
            ### Processing input/output
            if len(package_paths) == 1:
                logging.warn("[%s] Package has no provided modules" % idx)
                output = ""
                outerror = ""
            else:
                subproc = subprocess.Popen(
                    "../static-analysis/PackageImports",
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                )
                output, outerror = subproc.communicate(input=paths_for_input)
                output = re.sub(r"^\[.*\]", "", output).strip()
                output = re.sub(r"^\".*\"", "", output).strip()
                output = re.sub(r"^\[.*\]", "", output).strip()

            ### Persisting output
            if (not output and not outerror) or output:
                if not output and not outerror:
                    logging.warn("[%s] Empty result..." % idx)
                with open(pickle_file, "wb") as pickleFile:
                    pickle.dump(output, pickleFile)
            if outerror:
                logging.error("[%s] subproc Unexpected error : %s" % (pkg, outerror))

        except Exception as e:
            logging.error("[%s] Unexpected error : %s" % (pkg, str(e)))
    else:
        logging.info("[%s] Unpickling precomputed result %s" % (idx, pickle_file))
        try:
            with open(pickle_file, "rb") as pickleFile:
                output = pickle.load(pickleFile)
        except Exception as e:
            logging.error("[%s] Error unpickling %s" % (idx, pickle_file))

    logging.debug("[%s] Result: %s" % (idx, output))
    packageImports[pkg] = output
    logging.info("[%s] Done (%s/%s)" % (pkg, pkgNum, pkgTotal))
    pkgNum += 1

#################################################################################################################
## Join results and serialize resulting dataframe

logging.info("Merging Results")
moduleImports = []


logging.info("len(listToProcess): %s" % len(listToProcess))
logging.info("len(packageImports): %s" % len(packageImports))

for idx in listToProcess:
    moduleImports.append(packageImports[idx].split(","))

df_paths["imported-modules"] = pd.Series(moduleImports, index=df_paths.index)
df_paths.to_pickle("%s-with-imports.df" % args.df.replace(".df", ""))

logging.info("Finishing work at %s" % str(datetime.now()))