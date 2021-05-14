import pandas as pd
import numpy as np

lts_list = ['0-7', '2-22', '3-22', '6-35', '7-24', '9-21', '11-22', '12-14', '12-26', '13-11', '13-19', '14-27', '15-3', '16-11']

# returns a list with all the existing packages in some version of LTS
def get_all_time_packages(df_list):
    all_packages = set()
    for df in df_list:
        lts_packages = set(df['package'])
        all_packages = all_packages.union(lts_packages)

    return list(all_packages)

# return a DataFrame of versions of each package by LTS 
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

# return dictionary of top used packages unordered
def get_pkgs_usage_count(df):
    pkgs = {}
    
    for i, row in df.iterrows():        
        for dependency in (list(set(row['deps']))):
            if(not dependency in pkgs):
                pkgs[dependency] = 1
            else:
                pkgs[dependency] += 1
    
    return pkgs

# receives by parameter a list of packages and the DataFrame of an LTS. Returns a list of packages that do not belong to that selection
def get_packages_out_of_stackage(pkgs, df):
    all_pkgs = list(df['package'])
    return list(filter(lambda pkg: pkg not in all_pkgs, pkgs))

# create a dict of lts
def create_lts_obj():
    data = {}
    for idx, lts in enumerate(lts_list):
        data[lts] = []
    return data

# 
def get_pkgs_out_transitively(df_list):
    visited = {}
    def dfs(lts, pkg):
        visited[pkg] = True
        if not pkg in list(df['package']):
            return False

        for dependency in df[df['package'] == pkg]['deps'][0]:
            if visited[pkg] != True:
                dfs(dependency, pkg)

        return True


    out_transitive_pkgs = create_lts_obj()
    for i, df in enumerate(df_list):
        visited = {}
        aux_out_transitive_pkgs = []

        for idx, row in df.iterrows():    
            for dependency in (list(set(row['deps']))):
                if not dfs(lts_list[i], dependency):
                    aux_out_transitive_pkgs.append(row['package']) 

        print(f"{lts_list[i]} processed")
        out_transitive_pkgs[lts_list[i]] = len(set(aux_out_transitive_pkgs))
    
    return out_transitive_pkgs

def get_update_count_df(df_list, versions_df):
    def last_update(row):
        for value in reversed(row):
            if isinstance(value, int) and value >= 0:
                return value
            
        return -1

    def was_updated(version_list, version, idx):
        if idx == 0:
            return True
        
        for past_version in reversed(version_list[:idx]):
            if version != "":
                return past_version != version 
                
        return False

    pkgs = get_all_time_packages(df_list)
    df = pd.DataFrame(index=pkgs, columns=lts_list)

    for i, row in df.iterrows():
        row_versions = versions_df[versions_df.index == row.name].values[0]
        
        for idx, version in enumerate(row_versions):
            if version == "":
                row.values[idx] = -1
                continue
            
            last_value = last_update(row.values)
            row.values[idx] = last_value + 1 if was_updated(row_versions, version, idx) else last_value
        
    return df.replace(-1, 0)


def get_count_updated_packages_by_lts(df_list, df):
    count_updated_packages_by_lts = create_lts_obj()
    for idx, lts in enumerate(lts_list):
        count_updated_packages_by_lts[lts] = 0
        if idx == 0:
            count_updated_packages_by_lts[lts] = 0
            continue
        
        for i, actual_version in enumerate(df[lts]):
            pkg = df.iloc[i].name
            last_version = df[lts_list[idx-1]].iloc[i]
            
            if actual_version == last_version+1:
                count_updated_packages_by_lts[lts] += 1

    for idx, lts in enumerate(count_updated_packages_by_lts):
        if idx == 0:
            count_updated_packages_by_lts[lts] = 0
        else:
            count_updated_packages_by_lts[lts] = count_updated_packages_by_lts[lts] * 100 / len(df_list[idx - 1])
    
    del count_updated_packages_by_lts['0-7']
    return count_updated_packages_by_lts


def build_mtl_continuity_matrix(df_list, pkgs):
    df = pd.DataFrame(index=pkgs, columns=lts_list)

    for i, row in df.iterrows():
        for j, lts in enumerate(lts_list):
            state = 0
            package = df_list[j].loc[df_list[j]['package'].isin([row.name])]

            if(not package.empty):
                state = 1
                [use_mtl] = package['mtl-direct'].values
                if(use_mtl == 1):
                    state = 2
            
            df.at[row.name, lts] = float(state)

    for idx, lts in enumerate(lts_list):
            df[lts] = pd.to_numeric(df[lts]) 
            
    return df


def get_added_packages_mtl_by_lts(continuity_df):
    count = list(np.zeros(len(lts_list)))

    for i, row in continuity_df.iterrows():
        for j, lts in enumerate(lts_list):
            if(row[lts] == 2):
                if(j == 0):
                    count[j] += 1
                elif(row[j-1] == 0):
                    count[j] += 1
    
    return count


def get_removed_packages_mtl_by_lts(continuity_df):
    count = list(np.zeros(len(lts_list)))
    
    for i, row in continuity_df.iterrows():
        for j, lts in enumerate(lts_list):
            if(j > 0):
                if(row[j] == 0 and row[j-1] == 2):
                    count[j] += 1

    return count


def get_packages_started_use_mtl(continuity_df):
    count = list(np.zeros(len(lts_list)))
    
    for i, row in continuity_df.iterrows():
        for j, lts in enumerate(lts_list):
            if(j == 0 and row[j] == 2):
                count[j] += 1

            if(j > 0):
                if(row[j] == 2 and row[j-1] == 1):
                    count[j] += 1

    return count


def get_packages_stopped_use_mtl(continuity_df):
    count = list(np.zeros(len(lts_list)))
    
    for i, row in continuity_df.iterrows():
        for j, lts in enumerate(lts_list):
            if(j > 0):
                if(row[j] == 1 and row[j-1] == 2):
                    count[j] += 1
                    
    return count

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
    "Control.Monad.Writer.Strict"
]

mtl_monads = ['Continuation', 'Error', 'Except', 'Identity', 'List', 'RWS', 'Reader', 'State', 'Trans', 'Writer']

def usage_combination_to_string(usage_vector):
    letters = ('C', 'E', 'I', 'L', 'R', 'S', 'T', 'W', 'X', 'Z')    
    combination = "".join(list(map(lambda x: x[1] if x[0] == 1 else "", zip(usage_vector, letters))))
    if combination == "":
        combination = "None"
    return combination

def compute_monad_usage_by_df(df):
    mtl_cont = mtl_modules[0:2]
    mtl_error = mtl_modules[2:4]
    mtl_except = mtl_modules[4:5]
    mtl_identity= mtl_modules[5:6]
    mtl_list = mtl_modules[6:7]
    mtl_rws = mtl_modules[7:11]
    mtl_reader = mtl_modules[11:13]
    mtl_state = mtl_modules[13:17]
    mtl_trans = mtl_modules[17:18]
    mtl_writer = mtl_modules[18:]    
    
    df.loc[df.index, 'Continuation'] = df[mtl_cont].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Error'] = df[mtl_error].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Except'] = df[mtl_except].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Identity'] = df[mtl_identity].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'List'] = df[mtl_list].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'RWS'] = df[mtl_rws].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Reader'] = df[mtl_reader].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'State'] = df[mtl_state].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Trans'] = df[mtl_trans].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Writer'] = df[mtl_writer].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'MonadsUsed'] = df[mtl_monads].sum(axis=1)
    
    df.loc[df.index, 'MonadsUsedVector'] = df.apply(
        lambda row: (
            row["Continuation"],
            row["Error"],
            row["Identity"],
            row["List"],
            row["Reader"],
            row["State"],
            row["Trans"],
            row["Writer"],
            row["Except"],
            row["RWS"]
        ), 
        axis = 1
    )
    
    df.loc[df.index, 'MonadsUsedCode'] = df.apply(lambda row: usage_combination_to_string(row['MonadsUsedVector']), axis = 1)
    return df