import zipfile
import h5py
import sys
PROJECT_ROOT = "/Users/User1/DS/aibs/"
sys.path.append(PROJECT_ROOT)
from src import swcfunctions


def get_zipped_data(zfile_path, string):
    """"""
    archive = zipfile.ZipFile(zfile_path)
    # print(archive)
    files = list(filter(lambda x: string in x.filename,  archive.filelist))
    filenames = []
    for b in files:
        filenames.append(b.filename)
    return filenames
