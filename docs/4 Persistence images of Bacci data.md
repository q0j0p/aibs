
# Persistence images for neurons in the "Bacci" archive (neuromorpho.org) 

```python
import pymongo
import sys, os
import numpy as np
from sklearn.neighbors import KernelDensity 
sys.path.append('../')
from src import swcfunctions
import seaborn as sns
import matplotlib.pyplot as plt

%matplotlib inline

client = pymongo.MongoClient(host="mongodb://localhost/27017/")
db = client.aibs
db.collection_names()
```
    ['nmorpho', 'features', 'morphology', 'persistence_barcodes', 'neurons']

```python
bacci_swc_files = os.listdir('../data/Bacci/CNG version/')
```

```python
pbcodes = {}
```

```python
skiprows={}
```


```python
# for i, f in enumerate(bacci_swc_files): 
#     name = f.split('.')[0]
#     print(i,name)
#     path = '../data/bacci/CNG version/'+f
#     skiprows[name]=(int(input(prompt=swcfunctions.NTree.preview_file(path))))
#     ntree = swcfunctions.NTree(path,skiprows=skiprows[name])
#     print('ntree created')
# #    ntree.preview_file()
#     pbcodes[name] = ntree.get_persistence_barcode()
#     print('barcode created')
skiprows = {'A090622': 7, 'A090909': 7, 'A091109': 7, 'A81212': 7, 'B091130': 7, 'C091109': 7, 'C091118': 7, 'C101118': 7, 'C81113': 7, 'D090910': 9, 'D091030': 7, 'D90203': 9, 'E091118': 7, 'E100616': 7, 'F091109': 7, 'F091118': 7, 'F091130': 7, 'F100616': 7, 'G90206': 7, 'H091127-1': 7, 'H091127-2': 6}
for i, f in enumerate(bacci_swc_files): 
    name = f.split('.')[0]
    print(i,name)
    path = '../data/bacci/CNG version/'+f
#     skiprows[name]=(int(input(prompt=swcfunctions.NTree.preview_file(path))))
    ntree = swcfunctions.NTree(path,skiprows=skiprows[name])
    print('ntree created')
#    ntree.preview_file()
    pbcodes[name] = ntree.get_persistence_barcode()
    print('barcode created')
```


```python
num_cells = len(pbcodes)
cell_name = [a for a in list(pbcodes.keys())]
```


```python
X_grid, Y_grid = np.mgrid[0:600:400j,0:600:400j] 
grid = np.vstack([X_grid.ravel(),Y_grid.ravel()])
Zs = {}
```

```python
for i, a in enumerate(pbcodes): 
    
    val = np.array([*zip(*pbcodes[a])])
    skl_kernel = KernelDensity(bandwidth=43.48)
    skl_kernel.fit(val.T)
    Zs[a] = np.exp(skl_kernel.score_samples(grid.T))
```


```python
# Retrieve cell images from source 
png_urls = {a['neuron_name']:a['png_url'] for a in db.nmorpho.find({'archive':"Bacci"})}
```


```python
from PIL import Image
import requests 
```


```python
fig, ax = plt.subplots(21,2,figsize=(10,105))
axs = ax.flatten()
for i in range(len(cell_name)): 
    name = cell_name[i]
    axs[2*i].imshow(Image.open(requests.get(png_urls[name], stream=True).raw))
    axs[2*i].set_title(name)
    v0,v1 = np.array([*zip(*list(pbcodes[name]))])
    axs[2*i+1].imshow(np.rot90(Zs[name].reshape(400,-1)), cmap=plt.cm.RdYlBu_r, extent=[0, 600, 0, 600])
    axs[2*i+1].plot( v0, v1, 'k.', markersize=4)
    axs[2*i+1].set_xlim([0, 600])
    axs[2*i+1].set_ylim([0, 600])
```


![png](4%20Persistence%20images%20of%20Bacci%20data_files/4%20Persistence%20images%20of%20Bacci%20data_12_0.png)

