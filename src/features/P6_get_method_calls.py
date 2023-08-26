from logging import log
from subprocess import PIPE
import subprocess
import pandas as pd
import numpy as np
import os

import sys #pleger
packageInfoJSONBinary = '../parse/PackageInfoJSON' + ('.exe' if sys.plataform == 'Win32' else '')  #pleger path for different os


def get_methods_calls(df_file, logging):

    df = pd.read_pickle(df_file)

    df["files-info"] = str(np.nan)

    for index, pkg in df.iterrows():
        logging.info("##################################")
        logging.info(f"################# {index}")
        logging.info("##################################")

        provided_modules_found = pkg["provided-modules-found"]
        main_modules_found = pkg["main-modules-found"]
        cabal_file = pkg["cabal-file"].replace('\\', '/')
        logging.debug(pkg["provided-modules-found"])
        path_list = []

        path_list.append(cabal_file)

        for path in main_modules_found:
            path_list.append(path.strip())

        for (module, path) in provided_modules_found:
            path_list.append(path.strip())

        logging.debug('Starting Parse')
        paths_for_input = "\n".join(path_list)
        logging.debug(paths_for_input)
        complated_process = subprocess.run(
            os.path.join(os.path.dirname(__file__),
                         packageInfoJSONBinary), #pleger 
            stdout=PIPE,
            input=paths_for_input,
            text=True
        )
        logging.debug('Finishing Parse')

        output = complated_process.stdout

        df.at[index, "files-info"] = output
        logging.debug(output)

    df.to_pickle(df_file)
    logging.info("Finishing get methods")
    return df_file
