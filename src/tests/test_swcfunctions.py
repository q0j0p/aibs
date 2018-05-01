import pytest
import sys
import numpy as np

sys.path.append('../..')
from nid.swcfunctions import *

@pytest.fixture
def ntree1(testdata='data/test_swc_data.swc'):
    return NTree(testdata,skiprows=7)

def test_ntree_df(ntree1):
    assert isinstance(ntree1.df, type(pd.DataFrame()))
    assert ntree1.df.ix[0,'parent']==-1

def test_ntree_pbc(ntree1):
    assert isinstance(ntree1.get_persistence_barcode(),list)

def test_ntree_get_terminal_nodes(ntree1):
    assert isinstance(ntree1.get_terminal_nodes(),np.ndarray)
