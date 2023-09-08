#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from datetime import datetime

import os
import pickle
import pandas as pd
import subprocess
from subprocess import PIPE
import re

import sys #pleger
packageImportBinary = '../parse/PackageImports' + ('.exe' if sys.platform == 'Win32' else '') #pleger path for different os


###########################################################################################
# This script processes each package in the dataframe, parsing all their provided modules
# to determine all imported modules in each package. The parsing and extraction is
# performed by the PackageImport.hs program
##


def construct_df_with_imports(df_file, logging):
    df = pd.read_pickle(df_file)
    output = ''
    packageImports = {}
    pickle_file_pattern = "./pickles/pkg_imports_%s.pickle"

    pkgNum = 1
    logging.info("Starting work at %s" % str(datetime.now()))
    for idx, row in df.iterrows():
        logging.info("[%s] Processing" % idx)

        # to do: change the path by OS

        pkg, mods, mains, cabal_file = (
            idx,
            list(map(lambda x: x[1], row["provided-modules-found"])),
            list(
                map(lambda x: x, row["main-modules-found"])),
            df.loc[idx]["cabal-file"].replace('\\', '/'),
        )
        package_paths = [cabal_file] + mods + mains
        paths_for_input = "\n".join(package_paths)

        logging.debug(
            "[%s] Input paths (%d):\n%s" % (
                idx, len(package_paths), paths_for_input)
        )

        pickle_file = str(pickle_file_pattern % idx)

        if not os.path.isfile(pickle_file):
            try:
                # Processing input/output
                if len(package_paths) == 1:
                    logging.warn("[%s] Package has no provided modules" % idx)
                    output = ""
                    outerror = ""
                else:
                    complated_process = subprocess.run(
                        os.path.join(os.path.dirname(__file__),
                                     packageImportBinary), #pleger
                        stdout=PIPE,
                        input=paths_for_input,
                        text=True
                    )
                    output = complated_process.stdout
                    output = re.sub(r"^\[.*\]", "", output).strip()
                    output = re.sub(r"^\".*\"", "", output).strip()
                    output = re.sub(r"^\[.*\]", "", output).strip()

                # Persisting output
                if (not output and not outerror) or output:
                    outerror = "" #pleger (PATCH TO PREVENT EXCEPTIION)
                    if not output and not outerror:
                        logging.warn("[%s] Empty result..." % idx)
                    with open(pickle_file, "wb") as pickleFile:
                        pickle.dump(output, pickleFile)
                if outerror:
                    logging.error("[%s] subproc Unexpected error : %s" %
                                  (pkg, outerror))

            except Exception as e:
                logging.error("[%s] Unexpected error : %s" % (pkg, str(e)))
        else:
            logging.info("[%s] Unpickling precomputed result %s" %
                         (idx, pickle_file))
            try:
                with open(pickle_file, "rb") as pickleFile:
                    output = pickle.load(pickleFile)
            except Exception as e:
                logging.error("[%s] Error unpickling %s" % (idx, pickle_file))

        logging.debug("[%s] Result: %s" % (idx, output))
        packageImports[pkg] = output
        logging.info("[%s] Done (%s/%s)" % (pkg, pkgNum, len(df)))
        pkgNum += 1

    #################################################################################################################
    # Join results and serialize resulting dataframe

    logging.info("Merging Results")
    moduleImports = []

    logging.info("len(listToProcess): %s" % len(df))
    logging.info("len(packageImports): %s" % len(packageImports))

    logging.debug(packageImports)
    for idx, row in df.iterrows():
        moduleImports.append(packageImports[idx].split(","))

    df["imported-modules"] = pd.Series(
        moduleImports, index=df.index)
    df.to_pickle("%s-with-imports.df" % df_file.replace(".df", ""))

    logging.info("Finishing work at %s" % str(datetime.now()))
    logging.debug(df["imported-modules"])

    return "%s-with-imports.df" % df_file.replace(".df", "")
