import zipfile
import swcfunctions
import h5py
PROJECT_ROOT = "/Users/User1/DS/aibs/"
SPECIES = 'drosophila melanogaster'

def get_zipped_data(zfile_path, string="CNG version"):
    """"""
    archive = zipfile.ZipFile(zfile_path)
    print(archive)
    cng_version_files = list(filter(lambda x: string in x.filename,  archive.filelist))
    for b in cng_version_files:
        print(b.filename)
        with open('tmp.swc', 'wb') as tmp_swcfile:
            tmp_swcfile.write(archive.read(b))

        #pdb.set_trace()
#        prev_file = swcfunctions.NTree.preview_file('tmp.swc')
        try:
            ntree = swcfunctions.NTree("tmp.swc")

            print(ntree.skiprows)
            data = ntree.get_persistence_barcode()
            pathlist = b.filename.split("/")
            labname = pathlist[0]
            cellname = pathlist[-1].split(".")[0]
            print(f"{labname}/{cellname}")

            with h5py.File(f"{PROJECT_ROOT}/data/{SPECIES}.h5", 'a') as h5f:
                h5f.create_dataset(f"{labname}/{cellname}", data=data)
        except Exception as e:
            print(f"Error in {b.filename}\n\t{e}")
