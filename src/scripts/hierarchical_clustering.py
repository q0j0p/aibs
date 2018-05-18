import sys, os
from csv import reader
import numpy as np
import h5py
import zipfile
from scipy.cluster import hierarchy
import matplotlib.pyplot as plt
sys.path.append("..")
import src
from src.utils import expts
from src.utils import zipfiles
from src import swcfunctions
from src import neuroncollector



class TheExpt(expts.Expt):
    error_files = []
    def pick_neurons_randomly(self, n, idfilepath, seed=44):
        """Given .tsv file of neuron_ids, randomly select n neurons (no replaement)"""
        neuron_dict = {}
        with open(idfilepath, 'r') as f:
            next(f)
            for r in reader(f, delimiter="\t"):
                neuron_dict[r[1]]= [r[0],r[2],r[3],r[4]]
        neurons = np.array(list(neuron_dict.keys()))
        np.random.seed(seed)
        neurons = np.random.choice(neurons, replace=False,size=n)
        self.neuron_list = list(neurons)

    def get_pbcode_data(self, h5_filepath):
        """"Fetch the right .swc file as io buffer"""
        if not os.path.exists(h5_filepath):
            f = h5py.File(h5_filepath,"w")
            f.close()
        self.h5f = h5_filepath

        # names of all .zip files containing .swc files
        zipfile_names = os.listdir(src.PROJECT_ROOT+"/raw/data/swc_data/")

        # (zipfilename, swcfilepath) of all .swc files stored in  "CNG version/" in .zip files
        swcfile_list = []
        for a in zipfile_names:
            swcfile_list.append((a, zipfiles.get_zipped_data(f"{src.PROJECT_ROOT}/raw/data/swc_data/{a}", string="CNG version")))

        # neuron_name : swc_filename
        neuron_dict = {}
        for a in self.neuron_list:
            for b in list(filter(lambda x: a in "".join(x[1]), swcfile_list)):
                neuron_dict[a] = b[0]

        swc_gen = self.generate_swc_file_buffer(neuron_dict)
        return swc_gen

    def generate_swc_file_buffer(self, neuron_dict):
        """Find the appropriate file corresponding to neuron_name in neuron_dict.keys() from .zip files"""
        for a in neuron_dict:
                if neuron_dict[a]:
                    archive = zipfile.ZipFile(src.PROJECT_ROOT+"/raw/data/swc_data/"+neuron_dict[a])
                    for b in filter(lambda x: ("CNG version" in x.filename) and (a in x.filename),  archive.filelist):
                        yield (b.filename,archive.read(b))
                else:
                    self.error_files.append(a)

    def get_pbcode_and_store_in_h5file(self, swc_gen):
        """Given .swc buffer, create ane save persistence barcode"""
        files_w_errors = []
        for a in swc_gen:
            #print(a[0])
            try:
                ntree = swcfunctions.NTree(a[1])
                data = ntree.get_persistence_barcode()
                pathlist = a[0].split("/")
                cellname = pathlist[-1].split(".")[0]
                #print(f"{cellname}")

                with h5py.File(self.h5f, "a") as h5f:
                    h5f.create_dataset(f"{cellname}/pbcode", data=data)
            except Exception as e:
                print(f"Error in {a[0]}\n\t{e}")
                files_w_errors.append(a[0])
        self.error_files.append(files_w_errors)

    def create_persistence_image_per_pbcode(self):
        """Create persistence image in respective hdf5 group"""
        with h5py.File(self.h5f, "a") as h5f:
            for i, a in enumerate(h5f.keys()):
                try:
                    Z = swcfunctions.create_persistence_image(h5f[f"{a}/pbcode"].value, plot=False)
                    h5f.create_dataset(f"{a}/pbimage", data=Z)
                    # print(f"{a}/pbimage created")
                except Exception as e:
                    print(e)


# Standalone script for hierchical clustering.  Can integrate l8r.
from scipy.cluster.hierarchy import dendrogram, linkage

def render_data(self):
    with h5py.File(self.h5f,"a") as h5f:
        X = np.zeros((len(h5f.keys()),160000))
        names = []
        for i,a in enumerate(h5f.keys()):
            X[i] = h5f[f"{a}/pbimage"].value.reshape(160000)
            names.append(a)
        neuron_dict = neuroncollector.ExtractData("drosophila melanogaster").get_project_info()
        celltypes = [neuron_dict[a][-1] for a in names]
    return X, celltypes

def plot_dendrogram(X,labels,**kwargs):
    Z = hierarchy.linkage(X, **kwargs)
    fig, ax = plt.subplots(1,1,figsize=(20,60))
    dendrogram = hierarchy.dendrogram(Z, ax=ax,labels=labels,leaf_font_size=16,
                            above_threshold_color='#bcbddc',
                            orientation='right')
    plt.show()

if __name__ == "__main__":
    pass
