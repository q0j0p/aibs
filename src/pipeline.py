import luigi
import luigi.contrib.hdfs
import luigi.contrib.s3
import os, sys
import inspect
import pymongo
import zipfile
import h5py
import boto3
import io
import pdb
PROJECT_ROOT = "/Users/User1/DS/aibs/"
sys.path.append(PROJECT_ROOT+"/src/")
import neuromorpho_api
import swcfunctions
import neuroncollector
"""
Pipeline
-------
1.  GetNeuronIDs - Acquire unique identifiers `neuron_id` from neurmomorpho.org database (alternately, complete metadata can be obtained from the API.)  Use the id to create HDF groups.
_.  Acquire files containing .swc files from neuromorpho.org and store in s3 bucket.  (Skip as I have them already)
2.  Extract swc data from zipped files, process and store as pandas dataframe in respective HDF group.
3.  Create persistence images as numpy arrans and store.
4.
"""
#
# class s3Config(luigi.Config):
#     bucket = luigi.Parameter()
#
# class s3Path(luigi.Task):
#     def output(self):
#         return luigi.contrib.s3.S3Target(
#             path='s3://{}/{}'.format(s3Config().bucket, s3Config.key()))

class Params(luigi.Config):
    species = luigi.Parameter()
    swc_dir = luigi.Parameter()
    zipfile_location = luigi.Parameter()



class GetNeuronIDs(luigi.Task):
    """Get IDs of neuron from source (neuromorpho.org)"""
    species = Params().species
    def requires(self):
        return None

    def run(self):
        ids = neuromorpho_api.get_neuron_ids(self.species)

        with self.output().open('w') as output_file:
            output_file.write(f"neuron_id\tneuron_name\tarchive\tbrain_region\tcell_type\n")

            for id in ids:
                id = utlis.filenames.clean_string(id)
                output_file.write("\n".join(f'{a[0]}\t{a[1]}\t{a[2]}\t{a[3]}\t{a[4]}' for a in id))
                output_file.write("\n")

    def output(self):
        path = PROJECT_ROOT + "data/"
        filename = self.species + "__ids.tsv"
        return luigi.LocalTarget(path + filename)

class ScrapeSwcFiles(luigi.Task):
    """Scrape data files from source and store as zipped file (per neuromorpho settings)"""
    zipfile_location = Params().zipfile_location

    def run(self):
        """Scrape code"""
        pass

    def output(self):
        if zipfile_location == "local"
            return [luigi.LocalTarget(PROJECT_ROOT+"raw/data/swc_data/"+a) for a in os.listdir(PROJECT_ROOT+"raw/data/swc_data/")]

class GetNeuronData(luigi.Task):
    """Collect scraped data"""
    species = luigi.Parameter()
    store = "local"

    def requires(self):
        return GetNeuronIDs('drosophila melanogaster')


    def run(self):

        for out_dir in self.output():
            luigi.local_target.LocalFileSystem().mkdir(out_dir.path)

    def output(self):
        """"""
        path = PROJECT_ROOT + "data/" + self.species
        if self.store == "hdfs":
            filename = self.species + ".h5"
            return luigi.contrib.hdfs.HdfsTarget(path + filename, format=luigi.contrib.hdfs.format.PlainDir)

        if self.store == "local":
            with self.input().open('r') as input_file:
                ids = [a.strip().split('\t')[1] for a in input_file]
                return [luigi.LocalTarget(path+"/"+id) for id in ids[1:]]


#        return luigi.LocalTarget()

class GetZippedSwc(luigi.Task):
    """Get zipped swc files acquired from neuromorpho.org and store in HDF"""
    #swc_dir = luigi.Parameter()
    species = Params().species
    store = "local"
    def requires(self):
        return GetNeuronData(species = self.species)


    def run(self):
        # for a in os.abspath(os.listdir(self.swc_dir)):
        #     archive = zipfile.ZipFile(filepath)
        #     cng_version_files = list(filter(lambda x: "CNG version" in x.filename, [a for a in archive.filelist]))
        #     for a in cng_version_files:
        #         name = a.filename.split("/")[-1].split(".")[0]
        #         with h5py.File(f"{self.species}.h5", 'w') as h5f:
        #             h5f.create_group(name, data=a)
        # Not atomic, but can't do much right now
        # s3 = boto3.resource('s3')
        # bucket = s3.Bucket('neuromorphodata')
        # for a in bucket.objects.all():
        #
        #     archive = zipfile.ZipFile(io.BytesIO(a.get()["Body"].read()))
        #     print(archive)
        #     cng_version_files = list(filter(lambda x: "CNG version" in x.filename,  archive.filelist))
        #     for b in cng_version_files:
        #         with open('tmp.swc', 'wb') as tmp_swcfile:
        #             tmp_swcfile.write(archive.read(b))
        #         data = swcfunctions.NTree("tmp.swc").get_persistence_barcode()
        #         pathlist = b.filename.split("/")
        #         labname = pathlist[0]
        #         cellname = pathlist[-1].split(".")[0]
        #         with h5py.File(f"{self.species}.h5", 'w') as h5f:
        #             h5f.create_dataset(f"{labname}/{cellname}", data=data)

        for a in self.input():
            neuroncollector.ExtractData.get_zipped_data(a)

    def output(self):
        return luigi.contrib.hdfs.HdfsTarget(f"{PROJECT_ROOT}/data/{self.species}.h5")



class GetSwc(luigi.Task):
    """
    """
    swc_dir = Params().swc_dirname
    species= Params().species

    def requires(self):
            return GetNeuronIDs(self.species)

    def run(self):
        filenames = os.listdir(self.swc_dir)
        fn_parts = [filename.strip(".zip").split("__") for filename in filenames]

        with self.output().open("w") as output_file:
            output_file.write("\n".join(fn_part[-1] for fn_part in fn_parts))

    def output(self):
        path = PROJECT_ROOT + "data/"
        filename = self.species + "__swcs.tsv"
        return luigi.LocalTarget(path + filename)



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
