import argparse, logging, sys, copy, os
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("df", help="Dataframe file with package imports")
parser.add_argument("pkgs_path", help="Directory of packages")
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

df = pd.read_pickle(args.df)
pkgs_path = args.pkgs_path

for index, pkg in df.iterrows():
    provided_modules_found = pkg["provided-modules-found"]
    
    new_list = []
    for (module, path) in provided_modules_found: 
        path = path.replace("//", "/")
        path = path.replace("./StackageDownload", pkgs_path)
        new_list.append((module, path))
        
    df.at[index, "provided-modules-found"] = new_list

df.to_pickle(args.df)