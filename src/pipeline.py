import luigi
import os, sys
import inspect
import pymongo
import zipfile
import h5py
PROJECT_ROOT = "/Users/User1/DS/aibs/"
sys.path.append(PROJECT_ROOT+"/src/")
from src import neuromorpho_api
"""
Pipeline
-------
1.  GetNeuronIDs - Acquire unique identifiers `neuron_id` from neurmomorpho.org database (alternately, complete metadata can be obtained from the API.)  Use the id to create HDF groups.
_.  Acquire files containing .swc files from neuromorpho.org and store in s3 bucket.  (Skip as I have them already)
2.  Extract swc data from zipped files, process and store as pandas dataframe in respective HDF group.
3.  Create persistence images as numpy arrans and store.
4.
"""

class s3Config(luigi.Config):
    bucket = luigi.Parameter()
    key = luigi.Parameter()

class DataParams(luigi.Config):
    species = luigi.Parameter()
    swc_dir = luigi.Parameter()

class GetNeuronIDs(luigi.Task):
    """Get IDs of neurons to work on."""
    species = luigi.Parameter()
    def requires(self):
        return None

    def run(self):
        ids = neuromorpho_api.get_neuron_ids(self.species)

        with self.output().open('w') as output_file:
            output_file.write(f"neuron_id\tneuron_name\tarchive\tbrain_region\tcell_type\n")

            for id in ids:
                output_file.write("\n".join(f'{a[0]}\t{a[1]}\t{a[2]}\t{a[3]}\t{a[4]}' for a in id))
                output_file.write("\n")

    def output(self):
        path = PROJECT_ROOT + "data/"
        filename = self.species + "__ids.tsv"
        return luigi.LocalTarget(path + filename)

class GetZippedSwc(luigi.Task):
    """Get zipped swc files acquired from neuromorpho.org and store as """
    swc_dir = luigi.Parameter()
    def run(self):
        for filepath in os.abspath(os.listdir(self.swc_dir)):
            archive = zipfile.ZipFile(filepath)
            cng_version_files = list(filter(lambda x: "CNG version" in x.filename, [a for a in archive.filelist]))
            for a in cng_version_files:
                name = a.filename.split("/")[-1].split(".")[0]
                h5f = h5py.File(f"{name}.h5", 'w')
                h5f.create_dataset('dataset_1', data=a)

    def output(self):
        return luigi.contrib.hdfs.HdfsTarget(self.date.strftime('data/streams_%Y_%m_%d_faked.tsv'))

class GetSwcData(luigi.Task):
    """"""
    swc_dir = luigi.Parameter()
    def requires(self):
        return [ InputText(self.swc_dir + '/' + filename)
                for filename in listdir(self.input_dir) ]

    def run(self):
        for filepath in os.abspath(os.listdir(self.swc_dir)):
            archive = zipfile.ZipFile(filepath)
            cng_version = filter(lambda x: "CNG version" in x, [a.filename for a in archive.filelist])


class GetSwc(luigi.Task):
    """Data Collection
    This class represents something that was created elsewhere by an external process,
    so all we want to do is to implement the output method.
    """
    swc_dir = luigi.Parameter()
    species= luigi.Parameter()

    def requires(self):
            return GetNeuronIDs(self.species)

    def run(self):
        filenames = os.listdir(self.swc_dir)
        fn_parts = [filename.strip(".zip").split("__") for filename in filenames]

        # if self.output():
        #     option = "a"
        # else:
        #     option = "w"

        with self.output().open("w") as output_file:
            output_file.write("\n".join(fn_part[-1] for fn_part in fn_parts))

    def output(self):
        path = PROJECT_ROOT + "data/"
        filename = self.species + "__swcs.tsv"
        return luigi.LocalTarget(path + filename)


class s3Path(luigi.Task):
    def output(self):
        return luigi.contrib.s3.S3Target(
            path='s3://{}/{}'.format(s3Config().bucket, s3Config.key()))

class CollectData(luigi.Task):
    # report_date = luigi.DateParameter()
    def requires(self):
        return [morphodata, metadata
            ]

    def output(self):
        """Produce output to?"""

    def run(self):
        """create persistence barcodes"""



if __name__ == '__main__':
    luigi.run()
