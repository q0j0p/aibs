import pytest
import sys
import numpy as np
import os
sys.path.append('../..')
from src.swcfunctions import *



@pytest.fixture
def ntree(datadir=os.listdir("data/")):
    return [NTree(data) for data in datadir]

def test_ntree_df(ntree):
    for a in ntree:
        assert isinstance(ntree1.df, type(pd.DataFrame()))
        assert ntree1.df.ix[0,'parent']==-1

def test_ntree_pbc(ntree):
    for a in ntree:
        assert isinstance(ntree1.get_persistence_barcode(),list)

def test_ntree_get_terminal_nodes(ntree):
    for a in ntree:
        assert isinstance(ntree1.get_terminal_nodes(),np.ndarray)
