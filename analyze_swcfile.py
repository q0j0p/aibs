import pandas as pd
import numpy as np
import collections

"""These functions use zero-indexing (arrays always start at zero), regardless of the .swc index"""
def preview_file(swcfile, rows=10):
    """Preview swc header and first few lines"""
    with open(swcfile, 'r') as f:
        print "First {} lines of `{}`:\n".format(rows, swcfile)
        for row in f.readlines()[:rows]:
            print "\t",row

def load_to_dataframe(swcfile, skiprows=1, sep=' '):
    """Load swc file to pandas dataframe and return dataframe
    Converts one-index swc to zero index.  """
    n_df = pd.read_csv(swcfile, skiprows=skiprows, sep=sep,
                names=['index','type','x_coord','y_coord','z_coord','radius','parent']
                )
    if int(n_df.loc[1,'parent'])==1 & int(n_df.loc[0,'index'])==1:
        n_df.loc[1:,'parent']-=1
        n_df['index']-=1
        #n_df.iloc[1:,'parent']
    return n_df

def euc_distance_to_root(n_df, root=0): # root=1 for "one-index"
    """For each point, calculate euclidean distance to root (assume index=0);
    add as column euc_dist_root"""
    dist_coords = np.asarray(
        n_df.loc[:,['x_coord','y_coord','z_coord']] \
    -   n_df.loc[root,['x_coord','y_coord','z_coord']]
    )
    print dist_coords.shape
    #return np.sum(dist_coords * dist_coords, axis=1)**.5
    return np.linalg.norm(dist_coords, axis=1)

def distance_to_parent(n_df):
    """for each point, get distance to parent node; return array"""
    dist_coords = np.asarray(
        n_df.loc[:,['x_coord','y_coord','z_coord']] \
    -   n_df.loc[n_df.loc[:,'parent'],['x_coord','y_coord','z_coord']].values
    )
    return np.linalg.norm(dist_coords, axis=1)

def get_child_list(n_df):
    child_list = collections.defaultdict(list)
    for row in n_df.iterrows():
        child_list[int(row[1]['parent'])].append(row[0])
    return child_list

def get_termini(n_df):
    child_list = get_child_list(n_df)
    termini = list(set(n_df.index.values[1:]) - set(child_list.keys()))
    return termini

def get_branches(n_df):
    child_list = get_child_list(n_df)
    return [a for a in child_list if len(child_list[a]) > 1]

def get_path_to_root(n, path_to_root, n_df):
    """Given a point, return a list of points connecting to the root"""
    n = n_df.loc[n,'parent']
    if n != -1:
        path_to_root.append(n)
#        print n
        get_path_to_root(n, path_to_root, n_df)

    return path_to_root

def get_dist_to_root(n, n_df):
    """Given a point n, get distance to root using get_path_to_root"""
    path_array = np.asarray(get_path_to_root(n,[n],n_df),dtype=int)
    #print(path_array)
    return distance_to_parent(n_df)[path_array[:-1]].sum()
