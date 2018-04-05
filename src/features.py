import pymongo
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize
from bson import ObjectId, json_util
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error
import collections
import pprint

# Temporary global variables
client = pymongo.MongoClient('mongodb://localhost/:27017')
db = client.aibs
n_coll = db.neurons


def load_data():
    client = pymongo.MongoClient('mongodb://localhost/:27017')
    db = client.aibs
    n_coll = db.neurons
    n_df = pd.DataFrame({a['id']:a['ephys_features'][0] for a in n_coll.find()}).T
    n_df.reset_index(inplace=True)
    return n_df


def set_dtypes(df):
    """Set data types for all features
    """
    dtype = collections.defaultdict()
    dtype_dict = {'f':'float64',
                  'i':'int64',
                  'b':'bool',
                  's':'obj'}
    for a in df.columns:
        try:
            istring = raw_input("'{}' data type: ".format(a))
            df[a] = df[a].astype(dtype_dict[istring])
        except KeyError:
            print("input not in {}".format(dtype_dict))

    return df


def show_nans(df):
    """Observe nans
    """
    row_nas = df.T.isna().any()
    col_nas = df.isna().any()
    print"Rows with nans:", row_nas.sum()
    print"Columns with nans:",col_nas.sum()
    print"\n"
    for i,j in enumerate(df.isna().sum().items()):
        print i,j

def remove_nans(df,remove=[], drop_rows=True):
    """Appropriately remove nans"""
    df2 = df.drop(columns=df.columns[remove])
    if drop_rows:
        df2.dropna(inplace=True)
    return df2

def get_labels(df, labname):
    label=collections.defaultdict()
    for a in  df['index']:
        label[a] = n_coll.find({'id':a}).next()[labname]
    return label



def feature_importance(X, y, n_estimators=100, col_labels=None, importances=None, err=True):
    """Create a plot indicating feature importances

    Parameters
    ----------
    n_estimators : int
        number of estimators for random forest cf
    col_labels : dict
        column labels
    err : bool

    X : ndarray
        data
    y : ndarray
        label

    """

    cf = RandomForestClassifier(n_estimators=n_estimators)
    cf.fit(X, y)

    if isinstance(importances, type(None)):
        importances = cf.feature_importances_
        std = np.std([tree.feature_importances_ for tree in cf.estimators_], axis=0)

    idxs = np.argsort(importances)[::-1]

    if isinstance(col_labels, type(None)):
        col_labels = {}
    else:
        col_labels = {idx: label for idx, label in enumerate(col_labels)}

    print('Feature ranking:')
    for feat in range(importances.shape[0]):
        print("{}. {} ({})".format(feat+1, col_labels.get(idxs[feat], idxs[feat]), importances[idxs[feat]]))

    plt.figure(figsize=(10, 8))
    plt.title('Feature Importances')

    if err:
        plt.bar(range(importances.shape[0]), importances[idxs], yerr=std[idxs], align='center')
    else:
        plt.bar(range(importances.shape[0]), importances[idxs], align='center')
    xticks = [col_labels.get(idx, idx) for idx in idxs]
    plt.xticks(range(importances.shape[0]), xticks, rotation=-45)
    plt.xlim([-1, importances.shape[0]])
    plt.tight_layout()


def leave_one_out_feature_import(X, y, model, criterion=mean_squared_error, norm=True):
    ''' Drop each feature out and observe the effect on the specified criterion
    INPUT:
        X: numpy array
            Numpy array holding all features
        y: numpy array
            Numpy array of targets
        model: Model implementing .fit() and .predict()
        criterion: function evaluating a particular metric
            This function should be called like so: criterion(y_true, y_pred)
    OUTPUT:
        importances: numpy array
    '''
    model.fit(X, y)
    base = criterion(y, model.predict(X))
    importances = []

    for feat in range(X.shape[1]):
        X_sub = X[:, np.array([col != feat for col in range(X.shape[1])])]
        model.fit(X_sub, y)
        importances.append(abs(base - criterion(y, model.predict(X_sub))))

    importances = np.array(importances)
    if norm:
        importances = importances / np.sum(importances)
    return importances


def get_cell_types():
    """get
    """
    celltypes = list(nmorpho_coll.aggregate(
   [{"$group" : { "_id" : '$cell_type', "count" : {"$sum" : 1}}}]))
