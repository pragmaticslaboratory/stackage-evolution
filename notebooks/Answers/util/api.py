import pandas as pd
import numpy as np
import math
import operator
import re
from packaging import version
import glob

url = '../../data'
list_url = glob.glob(f"{url}/*")
lts_list = [lts.split('lts-')[1].replace('-','.') for lts in list_url]
lts_list = sorted(lts_list, key=lambda x: float(x))
lts_list = [lts.replace('.','-') for lts in lts_list]
lts_list.remove('18-18')
lts_list.insert(18,'18-18')
#lts_list = ['0-7', '2-22', '3-22', '6-35', '7-24', '9-21', '11-22', '12-14', '12-26', '13-11', '13-19', '14-27', '15-3', '16-11','16-31','17-2','18-6','18-8','18-18']

ops = {'>=': operator.ge, '>': operator.gt, '<=': operator.le, '<': operator.lt, '==': operator.eq}
def get_lts_list():
    
    return lts_list

# returns a list with all the existing packages in some version of LTS
def get_all_time_packages(df_list):
    all_packages = set()
    for df in df_list:
        lts_packages = set(df['package'])
        all_packages = all_packages.union(lts_packages)

    return all_packages

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

def get_pkgs_direct_dependency(df_list):  
    direct_dependency_pkgs = create_lts_obj()
    for i, df in enumerate(df_list):
        aux_direct_dependency_pkgs = []        
        count = 0
        for idx, row in df.iterrows():
            for dependency in (list(set(row['deps']))):
                count+=1
                aux_direct_dependency_pkgs.append(count)

        print(f"{lts_list[i]} processed")
        direct_dependency_pkgs[lts_list[i]] = len(set(aux_direct_dependency_pkgs))
        
    return direct_dependency_pkgs

def get_pkgs_indirect_dependency(df1):
    visited = {}
    def dfs(df1, pkg):
        visited[pkg] = True
        deps = df1[df1['package'] == pkg]['deps']
        if len(deps) > 0:
            for dependency in deps[0]: 
                if not dependency in visited:
                    dfs(df1, dependency)

        return 1
    for i, df in enumerate(df1):
        len_ind_deps = []
        for idx, row in df.iterrows():    
            total = 0
            for dependency in list(row['deps']):         
                dfs(df, dependency)
            for dependency in list(row['deps']):     
                if dependency in visited:
                    del visited[dependency]
            total = len(visited)
            visited = {}
            len_ind_deps.append(total)
        print(f"{lts_list[i]} processed")
        df['len_ind_deps'] = len_ind_deps
    return 1

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
    count_total_pkg = create_lts_obj()
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
            count_total_pkg[lts] = count_updated_packages_by_lts[lts]
            count_updated_packages_by_lts[lts] = count_updated_packages_by_lts[lts] * 100 / len(df_list[idx - 1])
    
    del count_updated_packages_by_lts['0-7']
    del count_total_pkg['0-7']
    list_count = [count_total_pkg,count_updated_packages_by_lts]
    return list_count


def build_continuity_matrix(df_list, pkgs, monad_direct):
    df = pd.DataFrame(index=pkgs, columns=lts_list)

    for i, row in df.iterrows():
        for j, lts in enumerate(lts_list):
            state = 0
            package = df_list[j].loc[df_list[j]['package'].isin([row.name])]

            if(not package.empty):
                state = 1
                [use_monad] = package[monad_direct].values
                if(use_monad == 1):
                    state = 2
            
            df.at[row.name, lts] = float(state)

    for idx, lts in enumerate(lts_list):
            df[lts] = pd.to_numeric(df[lts]) 
            
    return df


def get_added_packages_monad_by_lts(continuity_df):
    count = list(np.zeros(len(lts_list)))

    for i, row in continuity_df.iterrows():
        for j, lts in enumerate(lts_list):
            if(row[lts] == 2):
                if(j == 0):
                    count[j] += 1
                elif(row[j-1] == 0):
                    count[j] += 1
    
    return count


def get_removed_packages_monad_by_lts(continuity_df):
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

transfromers_modules = [
    "Control.Monad.Trans.Accum",
    "Control.Monad.Trans.Class",
    "Control.Monad.Trans.Cont",
    "Control.Monad.Trans.Except",
    "Control.Monad.Trans.Identity",
    "Control.Monad.Trans.Maybe",
    "Control.Monad.Trans.RWS",
    "Control.Monad.Trans.RWS.CPS",
    "Control.Monad.Trans.RWS.Lazy",
    "Control.Monad.Trans.RWS.Strict",
    "Control.Monad.Trans.Reader",
    "Control.Monad.Trans.Select",
    "Control.Monad.Trans.State",
    "Control.Monad.Trans.State.Lazy",
    "Control.Monad.Trans.State.Strict",
    "Control.Monad.Trans.Writer",
    "Control.Monad.Trans.Writer.CPS",
    "Control.Monad.Trans.Writer.Lazy",
    "Control.Monad.Trans.Writer.Strict"
]

other_modules = [
    "Control.Monad.Logger",
    "Control.Monad.Logger.CallStack",
    "Control.Monad.Free",
    "Control.Monad.Free.Ap",
    "Control.Monad.Free.Church",
    "Control.Monad.Free.Class",
    "Control.Monad.Free.TH"
]

mtl_monads = ['Continuation', 'Error', 'Except', 'Identity', 'List', 'RWS', 'Reader', 'State', 'Trans', 'Writer']
transformer_monads = ['State','Reader', 'Writer', 'Except', 'Identity', 'RWS', 'Class', 'Cont', 'Maybe',"Accum","Select"]

def make_columns_monad(df,monad):
    if monad == "transformer":
        df.loc[df.index, 'transformer-direct'] = df[transfromers_modules].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    elif monad == "other_modules":
        df.loc[df.index, 'other-direct'] = df[other_modules].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    
    return df

def usage_combination_to_string(usage_vector):
    letters = ('C', 'E', 'I', 'L', 'R', 'S', 'T', 'W', 'X', 'Z')    
    combination = "".join(list(map(lambda x: x[1] if x[0] == 1 else "", zip(usage_vector, letters))))
    if combination == "":
        combination = "None"
    return combination

def compute_other_monad_usage_by_df(df):
    module_logger = other_modules[0:1]
    module_free = other_modules[2:6]
    
    df.loc[df.index, 'Logger'] = df[module_logger].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Free'] = df[module_free].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    
    return df

def compute_monad_transformer_usage_by_df(df):
    tran_accum = transfromers_modules[0]
    tran_class = transfromers_modules[1]
    tran_cont = transfromers_modules[2]
    tran_except= transfromers_modules[3]
    tran_identity = transfromers_modules[4]
    tran_maybe = transfromers_modules[5]
    tran_rws = transfromers_modules[6:9]
    tran_reader = transfromers_modules[10]
    tran_select = transfromers_modules[11]
    tran_state = transfromers_modules[12:14]
    tran_writer = transfromers_modules[15:]    
    
    df.loc[df.index, 'Accum'] = df[tran_accum].apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Class'] = df[tran_class].apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Cont'] = df[tran_cont].apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Except'] = df[tran_except].apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Identity'] = df[tran_identity].apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Maybe'] = df[tran_maybe].apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'RWS'] = df[tran_rws].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Reader'] = df[tran_reader].apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Select'] = df[tran_select].apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'State'] = df[tran_state].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'Writer'] = df[tran_writer].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
    df.loc[df.index, 'MonadUsedTransformer'] = df[transformer_monads].sum(axis=1)
    
    return df

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

def diagram_box(list_deps):
    outlier_list = [[],[],[],[],[]]
    for idx, x in enumerate (list_deps):
        Q1 = 0
        Q2 = 0
        Q3 = 0
        LS = 0
        LI = 0
        IQR = 0
        outlier = 0
        LS_LIvalue = 0
        Q1value = 0
        Q2value = 0
        Q3value = 0
        N = len(x)
        if (math.trunc((N+1)/4)-((N+1)/4)) == 0:
            Q1 = x[int(((N+1)/4)-1)]
        else:
            i = math.trunc((N+1)/4)
            d = math.trunc((N+1)/4) - ((N+1)/4)
            Q1 = x[i-1] + (d *(x[i]-x[i-1]))

        if (math.trunc(3*(N+1)/4)-(3*(N+1)/4)) == 0:
            Q3 = x[int((3*(N+1)/4)-1)]
        else:
            i = math.trunc(3*(N+1)/4)
            d = math.trunc(3*(N+1)/4) - (3*(N+1)/4)
            Q3 = x[i-1] + d *(x[i]-x[i-1])

        if len(x)%2:            
            Q2 = x[round(N/2)-1]
        else:
            Q2 = (x[round(N/2)-1]+x[round(N/2)])/2
        IQR = Q3-Q1
        LI = Q1 - (1.5*IQR)
        LS = Q3 + (1.5*IQR)
        for j in range(len(x)):
            if LS <= x[j] or LI >= x[j]:
                outlier+=1
            if (LS > x[j] and Q3 < x[j]) or (LI < x[j] and Q1 > x[j]):
                LS_LIvalue+=1
            if Q3 >= x[j] and Q2 < x[j]:
                Q3value+=1
            if Q2 == x[j]:
                Q2value+=1
            if Q1 <= x[j] and Q2 > x[j]:
                Q1value+=1
        outlier_list[0].append(outlier*100/N)
        outlier_list[1].append(LS_LIvalue*100/N)
        outlier_list[2].append(Q3value*100/N)
        outlier_list[3].append(Q2value*100/N)
        outlier_list[4].append(Q1value*100/N)
    
    return outlier_list

def calculate_bottom(data, bar_idx):
    if bar_idx == 0:
        return 0
    
    cumsum = [0 for lts in lts_list]
    for idx in range(0, bar_idx):
        cumsum = list(map(operator.add, cumsum, data[idx]))
    return cumsum

def calculate_bottom_dict(data, keylist, bar_idx):
    if bar_idx == 0:
        return 0
    
    cumsum = [0 for lts in lts_list]
    for idx in range(0, bar_idx):
        cumsum = list(map(operator.add, cumsum, data[keylist[idx]]))
    return cumsum

def compare_range(v, range1, range2=None):
    (op1, v_range1) = range1
    if v_range1[-1] == "*":
        if len(v_range1) - 2 > len(v):
            print(
                "not supported case",
                {"version": v, "len(version)": len(v), "v_range1": v_range1, "len(v_range1)": len(v_range1) - 2},
            )
        v_range1 = v_range1.split(".")[:-1]
        v = ".".join(v.split(".")[0 : len(v_range1)])
        v_range1 = ".".join(v_range1)

    vrs = version.parse(v)
    vrs_range1 = version.parse(v_range1)

    if range2 is None:
        return ops[op1](vrs, vrs_range1)

    (op2, v_range2) = range2
    vrs_range2 = version.parse(v_range2)
    return ops[op1](vrs, vrs_range1) and ops[op2](vrs, vrs_range2)


def in_range(v, range):
    ranges = range.split(" && ")

    range1 = re.match("(.*?)(\d.*)", ranges[0]).groups()
    if len(ranges) == 1:
        return compare_range(v, range1)

    range2 = re.match("(.*?)(\d.*)", ranges[1]).groups()
    return compare_range(v, range1, range2)

def foo(df):
    df['dependencies_status'] = ''
    for idx, pkg in df.iterrows():
        dependencies_status = {}
        for version_range_depencency in pkg["version-range-deps"]:
            if len(version_range_depencency) != 2:
                # without dependencies
                continue

            (name, range) = version_range_depencency
            if range == "-any":
                dependencies_status[name] = "ANY"
                continue

            lts_pkg_index = df.index[df["package"] == name].tolist()
            if not lts_pkg_index:
                # package that doesn't exist in the LTS
                continue

            pkg_index = lts_pkg_index[0]
            lts_package_version = df.at[pkg_index, "version"]
            is_in_range = None

            if "||" in range:
                multiple_ranges = range.split(" || ")
                is_in_range = any(in_range(lts_package_version, r) for r in multiple_ranges)
                dependencies_status[name] = "IN_RANGE" if is_in_range else "OUT_RANGE"
            else:
                is_in_range = in_range(lts_package_version, range)
                dependencies_status[name] = "IN_RANGE" if is_in_range else "OUT_RANGE"
        df.at[idx,'dependencies_status'] = dependencies_status
        '''if any(dependencies_status[name] == "OUT_RANGE" for name in dependencies_status):
            out_range_dependencies = dict(filter(lambda status: status[1] == "OUT_RANGE", dependencies_status.items()))
            out_range_names = list(out_range_dependencies.keys())
            lts_dependencies_version = list(df[df["package"].isin(out_range_names)]["version"])
            ranges = dict(filter(lambda range: range[0] in out_range_names, pkg["version-range-deps"]))
            print(
                 {
                     "pkg": pkg["package"],
                     "deps": out_range_dependencies,
                     "lts_deps_version": lts_dependencies_version,
                     "ranges": ranges,
                 },
            )'''
