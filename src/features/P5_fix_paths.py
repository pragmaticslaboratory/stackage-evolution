import pandas as pd


def fix_paths(path_file, df_file, logging, lts):
    df = pd.read_pickle(df_file)

    for index, pkg in df.iterrows():
        provided_modules_found = pkg["provided-modules-found"]
        new_list = []
        for (module, path) in provided_modules_found:
            path = path.replace("//", "/")
            path = path.replace(lts, lts.replace(".", "-"))
            path = path.replace("./StackageDownload", path_file)
            new_list.append((module, path))

        df.at[index, "provided-modules-found"] = new_list

        main_modules_found = pkg["main-modules-found"]
        new_list = []
        for path in main_modules_found:
            path = path.replace("./StackageDownload", path_file)
            path = path.replace(lts, lts.replace(".", "-"))
            new_list.append(path)

        df.at[index, "main-modules-found"] = new_list

        cabal_file = pkg["cabal-file"].replace(
            "/Users/fruiz/Desktop/github/papers-stackage/pipelines/scripts/StackageDownload", path_file)
        cabal_file = cabal_file.replace(lts, lts.replace(".", "-"))
        df.at[index, "cabal-file"] = cabal_file

    df.to_pickle(df_file)
    logging.info("Finishing work of fix paths")

    return df_file
