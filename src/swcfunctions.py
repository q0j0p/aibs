# import pprint
import pandas as pd
import numpy as np
import collections
import functools
import operator
import subprocess

def preview_file(swcfile, rows=15):
    """Preview swc header and first few lines"""
    with open(swcfile, 'r') as f:
        print("First {} lines of `{}`:\n".format(rows, swcfile))
        for n, row in enumerate(f.readlines()[:rows]):
            print("{}\t{}".format(n,row))

def load_to_dataframe(swcfile, skiprows=None,
            names=['type','x_coord','y_coord','z_coord','radius','parent'],
            dtype={'index':'uint8','type':'uint8','parent':'int32'},
            sep=" ",
            **kwargs):
    """Load swc file to pandas dataframe and return"""
    n_df = pd.read_csv(swcfile, names=names,
                dtype=dtype, skiprows=skiprows, sep=" ",
                **kwargs
                )
    return n_df

def euc_distance_to_root(n_df, root_index=1):
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
    # if childlist.get(-1):
    #     del childlist[-1]
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


def memoize(obj):
    """cache output of functions for efficiency"""
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)
        return cache[args]
    return memoizer

class NTree(object):
    """This class generates morophology information from swc files.
    """
    def __init__(self, swcfile, skiprows=None, root_index=1):
        self.root_index = root_index
        if skiprows==None:
            cmd1 = ["grep", "^#", swcfile]
            cmd2 = ["wc", "-l"]
    #    print(cmd1, cmd2)
            grep = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
            out = subprocess.check_output(cmd2, stdin = grep.stdout)
            self.skiprows = int(out.strip())
        self.df = self.load_to_dataframe(swcfile, skiprows=self.skiprows, sep=" ")
        self.df['child_indices'] = self._get_child_list()
        self.df['euc_dist_to_root'] = self.get_euc_distance_to_root()
        self.branch_nodes = self.get_branch_nodes()
        self.terminal_nodes = self.get_terminal_nodes()

    @staticmethod
    def preview_file(swcfile, rows=15):
        preview_file(swcfile, rows)

    def load_to_dataframe(self,swcfile,skiprows, sep=" "):
        return load_to_dataframe(swcfile,skiprows=self.skiprows, sep=" ")

    def verify_swc_structure(self):
        assert self.df.iloc[0,5] == -1
#        assert self.df.shape[0] == self.df.loc[self.df.shape[0]-1,'pindex']

    def _get_child_list(self):
        """Returns child list as pandas series"""
        return self.df.merge(get_child_list(self.df),how='left',right_index=True,
            left_index=True).loc[:,['child_indices']]

    def get_branch_nodes(self):
        """Given df with child indices, returns numpy array of branch nodes"""
        branch_nodes = [1]
        for row in self.df.iterrows():
            if type(row[1]['child_indices']) == list:
                if len(row[1]['child_indices']) > 1:
                    branch_nodes.append(row[0])
        return np.array(branch_nodes)

    def get_terminal_nodes(self):
        """Given df with child indices, returns numpy array of terminal nodes"""
        terminal_nodes = []
        for row in self.df.iterrows():
            if type(row[1]['child_indices']) != list:
                terminal_nodes.append(row[0])
        return np.array(terminal_nodes)

    def get_euc_distance_to_root(self):
        return euc_distance_to_root(self.df,self.root_index)

    def get_lineage(self,l):
        """Given a node index, yield a generator that traces lineage to root,
        traversing branch nodes"""

        n = l
        lineage = [n]
        while n != -1:
            p = self.df.loc[n,'parent']
            if p in self.branch_nodes:
                lineage.append(p)
            n = p
        lineage.append(-1)
        yield lineage

    @memoize
    def get_parent_branch(self,l):
        """Get parent branch of l"""
        n = l
        while True:
            p = self.df.loc[n,'parent']
            if p in self.branch_nodes:
                return p
            if p == -1:
                return 1
            n = p
        return n

    @memoize
    def get_child_nodes(self,n):
        """Given a node, find its children (branches and leaves immediately downstream)"""
        assert n in self.branch_nodes

        child_nodes = []
        cl = collections.deque(self.df.loc[n,'child_indices'])
        while len(cl)>0:
            c = cl.pop()
            if any([(c in self.branch_nodes), (c in self.terminal_nodes)]):
                child_nodes.append(c)
            else:
                cl.extendleft(self.df.loc[c,'child_indices'])
        return child_nodes



    def get_subtree_leaves(self,n):
        """Given node index n, return list of leaves in subtree"""
        terminal_nodes = self.get_terminal_nodes()
        cl = self.df.loc[n,'child_indices']
        if type(cl)==list:
            node_list = collections.deque(cl)
        else:
            return [n]

        subtree_leaves = []
        while len(node_list) != 0:
            n = node_list.popleft()
            cl = self.df.loc[n,'child_indices']
            if type(cl)==list:
                if len(cl)>1:
                    node_list.extendleft(cl)
                elif len(cl) == 1:
                    node_list.appendleft(cl[0])
            else:
                subtree_leaves.append(n)
        return subtree_leaves


    def get_farthest_subtree_leaf_dist(self,n):
        """Given node index n, return distance of farthest leaf in subtree starting from n"""
        subtree_leaves= self.get_subtree_leaves(n)
        if len(subtree_leaves)==1:
            return self.df.loc[subtree_leaves,'euc_dist_to_root']
        else:
            return self.df.loc[subtree_leaves,'euc_dist_to_root'].sort_values()[-1:]


    def get_persistence_barcode(self):
        """Implement persistence barcode analysis"""
        D_t = []
        active_list = list(self.get_terminal_nodes())
        v_ = collections.defaultdict()
        for l in active_list:
            v_[l] = self.df.loc[l,'euc_dist_to_root']
        while self.root_index not in active_list:
            for l in active_list:
                p = self.get_parent_branch(l) #*make hash
                C = self.get_child_nodes(p) # immediate branches or leaves below p
                if all([n in active_list for n in C]):
                    vc_ = dict((k,v_[k]) for k in C)
                    c_m = max(vc_.items(), key=operator.itemgetter(1))[0]
                    active_list.append(p)
                    for c in C:
                        active_list.remove(c)
                        if c != c_m:
                            D_t.append((v_[c], self.df.loc[p,'euc_dist_to_root']))
                    v_[p] = v_[c_m]
        D_t.append((v_[self.root_index],self.df.loc[self.root_index,'euc_dist_to_root']))
        return D_t

    def barcode_density_profile(self):
        pass

    def plot_morphology(self):
        """Retrieve 2d snapshot if available (if not, render) and plot"""
        pass
    def plot_persistence_image(self):
        """"""
