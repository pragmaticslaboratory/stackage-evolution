import argparse
from subprocess import PIPE
import subprocess
import pandas as pd
import numpy as np
import os

parser = argparse.ArgumentParser()
parser.add_argument("df", help="Dataframe file with package imports")

args = parser.parse_args()
df = pd.read_pickle(args.df)

df["files-info"] = str(np.nan)

for index, pkg in df.iterrows():
    print("##################################")
    print(f"################# {index}")
    print("##################################")

    provided_modules_found = pkg["provided-modules-found"]
    main_modules_found = pkg["main-modules-found"]
    cabal_file = pkg["cabal-file"]

    path_list = []

    path_list.append(cabal_file)

    for path in main_modules_found:
        path_list.append(path.strip())

    for (module, path) in provided_modules_found:
        path_list.append(path.strip())

    paths_for_input = "\n".join(path_list)

    complated_process = subprocess.run(
        os.path.join(os.path.dirname(__file__), '../parse/PackageInfoJSON'),
        stdout=PIPE,
        input=paths_for_input,
        text=True
    )

    output = complated_process.stdout

    df.at[index, "files-info"] = output

df.to_pickle(args.df)