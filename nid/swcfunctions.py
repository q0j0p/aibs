# import pprint
import pandas as pd
import numpy as np
import collections

def preview_file(swcfile, rows=15):
    """Preview swc header and first few lines"""
    with open(swcfile, 'r') as f:
        print("First {} lines of `{}`:\n".format(rows, swcfile))
        for n, row in enumerate(f.readlines()[:rows]):
            print("{}\t{}".format(n,row))

def load_to_dataframe(swcfile, skiprows=1, sep=' ',dtype={'index':'uint8','type':'uint8','parent':'int8'}):
    """Load swc file to pandas dataframe and return"""
    n_df = pd.read_csv(swcfile, skiprows=skiprows, sep=sep, index_col=0,
                names=['type','x_coord','y_coord','z_coord','radius','parent']
                )
    return n_df

def euc_distance_to_root(n_df, root_index=0):
    """For each point, calculate euclidean distance to root (default root index=0);
    add as column euc_dist_root"""
    dist_coords = np.array(
        n_df.loc[:,['x_coord','y_coord','z_coord']] \
      - n_df.loc[root_index,['x_coord','y_coord','z_coord']],dtype=float)
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
    childlist = collections.defaultdict(list)
    for row in n_df.iterrows():
        childlist[int(row[1]['parent'])].append(row[0])
    del childlist[-1]
    childlist_df = pd.DataFrame(pd.Series(childlist))
    childlist_df.columns=['child_indices']
    return childlist_df

def get_termini(n_df):
    child_list = get_child_list(n_df)
    termini = set(n_df.index.values) - set(child_list)
    return termini

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
    path_array = np.asarray(get_path_to_root(n,[],n_df))
    return distance_to_parent(n_df)[path_array[:-1]].sum()

def get_persistence_barcode(tree):
    """Given swc, return persistence barcode
    """
    pass

class NTree(object):
    """This class generates morophology information from swc files.
    """
    def __init__(self,swcfile,skiprows=1,root_index=1):
        self.root_index = 1
        self.df = self.load_to_dataframe(swcfile,skiprows)
        self.df['child_indices'] = self._get_child_list()
        self.df['euc_dist_to_root'] = self.get_euc_distance_to_root()

    @staticmethod
    def preview_file(swcfile):
        preview_file(swcfile)

    def load_to_dataframe(self,swcfile,skiprows):
        return load_to_dataframe(swcfile,skiprows)

    def verify_swc_structure(self):
        assert self.df.iloc[0,5] == -1
#        assert self.df.shape[0] == self.df.loc[self.df.shape[0]-1,'pindex']

    def _get_child_list(self):
        """Returns child list as pandas series"""
        return self.df.merge(get_child_list(self.df),how='left',right_index=True,
            left_index=True).loc[:,['child_indices']]

    def get_branch_nodes(self):
        """Given df with child indices, returns numpy array of branch nodes"""
        branch_nodes = []
        for row in self.df.iterrows():
            if type(row[1]['child_indices']) == list:
                if len(row[1]['child_indices']) > 1:
                    branch_nodes.append(row[0])
        return np.array(branch_nodes)

    def get_terminal_nodes(self):
        """Given df with child indices, returns numpy array of branch nodes"""
        terminal_nodes = []
        for row in self.df.iterrows():
            if type(row[1]['child_indices']) != list:
                terminal_nodes.append(row[0])
        return np.array(terminal_nodes)

    def get_euc_distance_to_root(self):
        return euc_distance_to_root(self.df,self.root_index)

    def get_farthest_subtree_leaf_dist(self):
        pass

    def get_persistence_barcode(self):
        D_t = []
        active_list = list(self.get_terminal_nodes())
        v_l = collections.defaultdict()
        for l in active_list:
            v_l[l] = self.df.loc[n,'euc_dist_to_root']
        while 1 not in active_list:
            for l in active_list:
                p = self.df.loc[l,'parent']
                C = self.df.loc[p,'child_indices']
                if type(C) == list & all([n in active_list for n in C]):
                    c_m = self.df.loc[C,'euc_dist_to_root'].argmax()
                    active_list.append(p)
                    for c in C:
                        active_list.remove(c)
                        if c != c_m:
                            D_t.append((self.get_farthest_subtree_leaf_dist(c),
                                        self.df.loc[p,'euc_dist_to_root']))
        D_t.append(self.get_farthest_subtree_leaf_dist(1),self.df.loc[1,'euc_dist_to_root'])
        return D_t
