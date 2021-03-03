#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging, argparse, pickle, os, sys
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("df", help="Initial dataframe without package module paths")
parser.add_argument(
    "-v",
    "--verbose",
    help="Set log level to DEBUG to increase output verbosity",
    action="store_true",
)
parser.add_argument(
    "-w",
    "--warning",
    help="Set log level to WARNING to increase output verbosity",
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
    logging.basicConfig(level=logging.DEBUG)
elif args.quiet:
    logging.basicConfig(level=logging.ERROR)
elif args.warning:
    logging.basicConfig(level=logging.WARN)
else:
    logging.basicConfig(level=logging.INFO)

df = pd.read_pickle(args.df)

####################################################################################
## Takes as input the package dataframe, this script:
## - downloads and extracts the source code of each package
## - tries every combination of provided-module/src-dirs to establish the
##   paths of each provided module. This is necessary for parsing in the next steps.
## - downloads are stored in the HACKAGE_ROOT/HackageDownload folder.
## - if a package is already present, it is not downloaded again
##
## The resulting output is a package dataframe that holds the path of each
## provided module in every package.
##

### Package indexes for insertion into the generated dataframe
packageIdxProvidedModules = {}
packageIdxProvidedModulesFound = {}
packageIdxProvidedModulesNotfound = {}

packageIdxMainModules = {}
packageIdxMainModulesFound = {}
packageIdxMainModulesNotfound = {}

### Global statistics for sanity checking
totalProvidedModules = 0
totalProvidedModulesFound = 0
totalProvidedModulesNotFound = 0

totalMainModules = 0
totalMainModulesFound = 0
totalMainModulesNotFound = 0

### Process configuration
download_dir = os.path.join(
    os.getenv("STACKAGE_ROOT", "./"), "StackageDownload/lts-16.11"
)
filepath_pattern = "%s/%s/%s-%s/%s/%s"

listToProcess = df.index.tolist()
pkgTotal = len(listToProcess)
logging.info("Download dir: %s" % download_dir)

for idx in listToProcess:
    dfrow = df.loc[idx]
    pkg_path = os.path.join(download_dir, dfrow["package"], idx)

    logging.info("[%s-%s] Processing" % (dfrow["package"], dfrow["version"]))

    if not os.path.isdir(pkg_path):
        logging.warn("[%s] Package directory not found at %s" % (idx, pkg_path))
        continue

    ##### FIND PATHS FOR PROVIDED MODULES ###########################################################

    ### Cabal has a special Paths_* module used during builds
    ### https://stackoverflow.com/questions/21588500/haskell-cabal-package-cant-find-paths-module
    ### Other file extensions:
    ### - chs: for calling foreign C functions
    ## We omit .y .x .ly and .lx files (Happy and Alex) because we already processed them in the downloads
    # preprocExts = ["hsc", "gc", "chs", "y", "x", "ly", "lx" ]
    commonExts = ["hs", "lhs"]
    preprocExts = ["hsc", "gc", "chs"]

    pkgProvidedModules = dfrow["provided-modules"]
    pkgProvidedModulesFound = []
    pkgProvidedModulesNotFound = []
    for modname in pkgProvidedModules:

        # Omit ghc-specific "virtual" Paths_* modules
        if modname.startswith("Paths_"):
            logging.info("[%s] Omiting Paths_ module %s" % (idx, modname))
            pkgProvidedModulesNotFound.append(modname)
            continue

        found = False
        for ext in commonExts + preprocExts:
            normalized_mod_path = "%s.%s" % (modname.replace(".", "/"), ext)
            for srcdir in [""] + dfrow["src-dirs"]:
                modPath = filepath_pattern % (
                    download_dir,
                    dfrow["package"],
                    dfrow["package"],
                    dfrow["version"],
                    srcdir,
                    normalized_mod_path,
                )
                found = os.path.isfile(modPath)
                if found:
                    # break src dirs loop
                    pkgProvidedModulesFound.append((modname, modPath))
                    break
                logging.debug(
                    "[%s] Searching module %s in path %s" % (idx, modname, modPath)
                )
            if found:
                # break extensions loop
                break

        if not found:
            logging.warn("[%s] Provided module not found: %s" % (idx, modname))
            pkgProvidedModulesNotFound.append(modname)

    # Sanity check to spot weird modules
    # For debugging weird packages
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        pkgWeirdModules = [
            item
            for item in pkgProvidedModules
            if item not in (pkgProvidedModulesFound + pkgProvidedModulesNotFound)
        ]
        logging.info(">> [%s] WEIRD MODULES: %s" % (idx, pkgWeirdModules))
    assert len(pkgProvidedModules) == len(pkgProvidedModulesFound) + len(
        pkgProvidedModulesNotFound
    )

    # Global statistics for sanity checking
    totalProvidedModules = totalProvidedModules + len(pkgProvidedModules)
    totalProvidedModulesFound = totalProvidedModulesFound + len(pkgProvidedModulesFound)
    totalProvidedModulesNotFound = totalProvidedModulesNotFound + len(
        pkgProvidedModulesNotFound
    )

    # Updating package indexes for inserting into the dataframe
    packageIdxProvidedModules[idx] = pkgProvidedModules
    packageIdxProvidedModulesFound[idx] = pkgProvidedModulesFound
    packageIdxProvidedModulesNotfound[idx] = pkgProvidedModulesNotFound

    ##### FIND PATHS FOR MAIN MODULES ###########################################################
    ## Main packages already specify their file extension
    ##
    logging.info(
        "[%s] Updating main-modules paths with download dir %s" % (idx, download_dir)
    )
    pkgMainModules = dfrow["main-modules"]
    pkgMainModulesFound = []
    pkgMainModulesNotFound = []
    for mainMod in pkgMainModules:
        found = False
        for srcdir in [""] + dfrow["src-dirs"]:
            mainPath = os.path.join(
                download_dir,
                dfrow["package"],
                "%s-%s" % (dfrow["package"], dfrow["version"]),
                srcdir,
                mainMod,
            )
            found = os.path.isfile(mainPath)
            if found:
                pkgMainModulesFound.append(mainPath)
                break
        if not found:
            logging.warn("[%s] Main module not found: %s" % (idx, mainMod))
            pkgMainModulesNotFound.append(mainPath)

    # Sanity check to spot weird modules
    # For debugging weird packages
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        pkgWeirdMainModules = [
            item
            for item in pkgMainModules
            if item not in (pkgMainModulesFound + pkgMainModulesNotFound)
        ]
        logging.info(">> [%s] WEIRD MAIN MODULES: %s" % (idx, pkgWeirdMainModules))
    assert len(pkgMainModules) == len(pkgMainModulesFound) + len(pkgMainModulesNotFound)

    # Global statistics for sanity checking
    totalMainModules = totalMainModules + len(pkgMainModules)
    totalMainModulesFound = totalMainModulesFound + len(pkgMainModulesFound)
    totalMainModulesNotFound = totalMainModulesNotFound + len(pkgMainModulesNotFound)

    # Updating package indexes for inserting into the dataframe
    packageIdxMainModules[idx] = pkgMainModules
    packageIdxMainModulesFound[idx] = pkgMainModulesFound
    packageIdxMainModulesNotfound[idx] = pkgMainModulesNotFound

    ### Logging package finished processing
    logging.info(
        "[%s] Pkg Provided Modules Total: %d Found:%d NotFound: %d "
        % (
            idx,
            len(pkgProvidedModules),
            len(pkgProvidedModulesFound),
            len(pkgProvidedModulesNotFound),
        )
    )
    logging.info(
        "[%s] Pkg Main Modules Total: %d Found:%d NotFound: %d"
        % (
            idx,
            len(pkgMainModulesFound),
            len(pkgMainModulesFound),
            len(pkgMainModulesNotFound),
        )
    )
    logging.info("[%s] Done" % idx)

#################################################################################################################
## Join results and serialize resulting dataframe
logging.info(
    "#############################################################################"
)
logging.info(
    "Global Provided Modules Total: %d Found:%d NotFound: %d "
    % (totalProvidedModules, totalProvidedModulesFound, totalProvidedModulesNotFound)
)
logging.info(
    "Global Main Modules Total: %d Found:%d NotFound: %d"
    % (totalMainModules, totalMainModulesFound, totalMainModulesNotFound)
)

logging.info("Merging Results and creating new dataframe")

providedModulesFoundPaths = []
providedModulesNotFound = []
for idx in listToProcess:
    providedModulesFoundPaths.append(packageIdxProvidedModulesFound[idx])
    providedModulesNotFound.append(packageIdxMainModulesNotfound[idx])

df["provided-modules-found"] = pd.Series(providedModulesFoundPaths, index=df.index)
df["provided-modules-notfound"] = pd.Series(providedModulesNotFound, index=df.index)

mainModulesFoundPaths = []
mainModulesNotFound = []
for idx in listToProcess:
    mainModulesFoundPaths.append(packageIdxMainModulesFound[idx])
    mainModulesNotFound.append(packageIdxMainModulesNotfound[idx])

df["main-modules-found"] = pd.Series(mainModulesFoundPaths, index=df.index)
df["main-modules-notfound"] = pd.Series(mainModulesNotFound, index=df.index)

df.to_pickle("%s-with-paths.df" % args.df.replace(".df", ""))