import pandas as pd
import numpy as np

lts_list = [
    '0-7', 
    '2-22',
    '3-22',
    '6-35',
    '7-24',
    '9-21',
    '11-22',
    '12-14',
    '12-26',
    '13-11',
    '13-19',
    '14-27',
    '15-3',
    '16-11',
    '16-22'
]

# retorna una lista con todos los paquetes existentes en alguna version de LTS
def get_all_time_packages(df_list):
    all_packages = set()
    for df in df_list:
        lts_packages = set(df['package'])
        all_packages = all_packages.union(lts_packages)

    return list(all_packages)


def get_versions_df(df_list):
    pkgs = get_all_time_packages(df_list)
    df = pd.DataFrame(index=pkgs, columns=lts_list)

    for i, row in df.iterrows():
        for j, lts in enumerate(lts_list):
            version = ""
            aux_df = df_list[j]
            
            if(not aux_df.loc[aux_df['package'].isin([row.name])].empty):
                version = aux_df.loc[aux_df['package'] == row.name]['version'].values[0]

            df.at[row.name, lts] = str(version)
    
    return df
