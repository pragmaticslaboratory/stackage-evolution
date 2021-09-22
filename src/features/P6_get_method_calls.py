from subprocess import PIPE
import subprocess
import pandas as pd
import numpy as np
import os


def get_methods_calls(df_file, logging):

    df = pd.read_pickle(df_file)

    df["files-info"] = str(np.nan)

    for index, pkg in df.iterrows():
        logging.info("##################################")
        logging.info(f"################# {index}")
        logging.info("##################################")

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
            os.path.join(os.path.dirname(__file__),
                         'C:/Users/nicol/Documents/GitHub/stackage-evolution/src/parse/PackageInfoJSON.exe'),
            stdout=PIPE,
            input=paths_for_input,
            text=True
        )

        output = complated_process.stdout

        df.at[index, "files-info"] = output

    df.to_pickle(df_file)
    logging.info("Finishing get methods")
    return df_file
