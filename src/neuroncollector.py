
import time
import pymongo
import os, shutil, sys
import matplotlib.pyplot as plt
import matplotlib.image as mplimg
from csv import reader
#from urllib import urlencode
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import h5py
import zipfile

PROJECT_ROOT = "/Users/User1/DS/aibs/"

sys.path.append(PROJECT_ROOT)
from src import swcfunctions
from src.utils import zipfiles


PROJECT_NAME = 'aibs'
MONGODB_URI = 'mongodb://localhost:27017/'
MONGODB_NAME = 'aibs'
MACHINE_OPTIONS= ['mac', 'ubuntu']

class NeuroScraper(object):
    """Web scraping functions for neuromorpho.org data collection.

    """

    def __init__(self,
                 dbname=MONGODB_NAME,
                 browser="Firefox",
                 machine="mac",
                 url="http://neuromorpho.org/byspecies.jsp",
                 dest_directory="swc_data/"
                 ):
        try:
            self.mongoclient = pymongo.MongoClient(MONGODB_URI)
            print("Connected to {}".format(MONGODB_URI))
        except pymongo.errors.ConnectionFailure as e:
            print("Could not connect to MongoDB: %s".format(e))
        self.mongodbase = self.mongoclient[dbname]
        self.coll = self.mongodbase['members']
        self.browser = browser
        self.machine = machine
        self.abs_root_path = self.get_root_path() + "/"
        print("absolute path to project root directory:", self.abs_root_path)
        self.target_url = url
        self.raw_data_dir = self.abs_root_path + "raw/data/"
        self.download_dir = f"{self.raw_data_dir}scraper_tmp/"
        self.dest_directory = f"{self.raw_data_dir}{dest_directory}"
        self.species = None
        if self.browser == "Firefox":
            self.use_firefox()
        elif self.browser == "Phantom":
            self.use_phantom()

    def get_root_path(self):
        path_list = os.getcwd().split('/')
        abs_root_path = "/".join(path_list[:len(path_list)- [i for i,j in \
            enumerate(path_list[::-1]) if j==PROJECT_NAME][0]])
        return abs_root_path

    def use_firefox(self):
        """Launch scraper using firefox browser.

        """
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('browser.download.folderList', 2) # custom location
        self.profile.set_preference('browser.download.manager.showWhenStarting', False)
        self.profile.set_preference('browser.download.dir', self.download_dir)
        self.profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip')
        print(self.profile)
        if self.machine==MACHINE_OPTIONS[0]: # mac
            self.driver = webdriver.Firefox(firefox_binary=FirefoxBinary(
                firefox_path='/Applications/FirefoxESR.app/Contents/MacOS/firefox'), firefox_profile=self.profile)
        elif self.machine==MACHINE_OPTIONS[1]: # ubuntu
            #os.system("Xvfb :90 -ac &")
            os.system("export DISPLAY=:90")
            self.driver = webdriver.Firefox(firefox_binary=FirefoxBinary(
                firefox_path='/usr/bin/firefox'), firefox_profile=self.profile)
        self.get_page()

    def use_phantom(self):
        """Launch scraper using phantomjs- deprecated, use firefox."""
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        # settings to emulate my machine, which works
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML,\
            like Gecko) Chrome/56.0.2924.76 Safari/537.36/")
#        self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
        self.driver = webdriver.PhantomJS(executable_path='/usr/local/share/phantomjs-1.9.7-linux-x86_64/bin/phantomjs',desired_capabilities=dcap)
#        self.driver.implicity_wait(5)
        self.driver.set_window_size(839, 937)

    def get_page(self, url = None, get_screenshot=True, sleeptime=3):
        if url==None:
            url = self.target_url
        self.driver.get(url)
        if get_screenshot:
            self.save_and_show_screenshot()

    def save_and_show_screenshot(self):
        self.driver.get_screenshot_as_file(filename='sc.png')
        plt.figure(figsize=(10,10))
        img=mplimg.imread('sc.png')
        imgplot = plt.imshow(img)
        plt.show()

    def wait_and_rename_file(self, ddir, filename, dest_dir):
        """Monitor file download to directory and rename when finished (not foolproof)"""
        while(ddir == os.listdir(self.download_dir)):
            time.sleep(1)
        while(any(list(map(lambda x: x.endswith('part'), os.listdir(self.download_dir))))):
            time.sleep(1)
        filename1 = max([self.download_dir+f for f in os.listdir(self.download_dir)], key=os.path.getctime)
        destfname = utils.filenames.clean_string(filename)
        shutil.move(f"{filename1}",f"{dest_dir}{destfname}.zip")
        print(f"saved file {dest_dir}{destfname}.zip")



    def close_driver(self):
        self.driver.close()

    """
    FYI: The following functions are neuromorpho.org-specific!
    """

    def get_species(self, species_index=None):
        """Get list of web elements corresponding to species on neuromorpho.org"""
        speciess = self.driver.find_elements_by_class_name("species")
        print("Total number of species:", len(speciess))
        species_names = [a.get_attribute("name") for a in speciess]
        if species_index == None:
            print("Species names")
            for i,a in enumerate(species_names):
                print(i,a)
            species_index = int(input("Enter species index:"))
        print("clicking on {}".format(species_names[species_index]))
        speciess[species_index].click()
        return species_names[species_index]

    def get_species_source(self, id='drosophila melanogaster_chkbox'):
        """Get list of web elements corresponding to data source (labs) under species"""
        lab_names = [a.text for a in self.driver.find_elements_by_xpath("//font[@id='lvl2']")]
        labs = self.driver.find_elements_by_xpath("//input[@id='"+id+"']")
        print("Source names (count:{}):".format(len(labs)))
        for i,a in enumerate(labs):
            print(i,a.get_attribute("value"))
        return lab_names, labs

    def get_neuron_category(self,lab):
        """Get neuron category (brain region) under data source (lab)"""
        lab_id = lab.get_attribute("value")

        neuron_categories =  self.driver.find_elements_by_xpath("//input[@id='"+lab_id+"_chkbox']")
        neuron_category_names = [a.text for a in  self.driver.find_elements_by_xpath("//font[@id='lvl3']")]
        return neuron_category_names, neuron_categories

    def get_neuron_subcategory(self,neuron_category):
        """Get neuron sub-category(neuron type) under given neuron_category"""
        cat_id = neuron_category.get_attribute("value")
        neuron_subcategories = self.driver.find_elements_by_xpath(f"//input[@id='{cat_id}_chkbox']")
        neuron_subcategory_names = [a.text for a in  self.driver.find_elements_by_xpath("//font[@id='lvl4']")]
        return neuron_subcategory_names, neuron_subcategories

    def click_download_and_rename_when_finished(self, dest_dir, filename):
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        ddir_slist = os.listdir(self.download_dir)
        self.driver.find_element_by_name('yes').click()
        self.wait_and_rename_file(ddir_slist, filename, dest_dir)


    def get_swc_files(self):
        self.driver.get(self.target_url)

    def process_filenames(self, species, neuron_strings, lab_names, brain_region_names, neuron_subset_names):
        """Parse the desired filename from web element value by string matdh with name list"""
        new_filenames= {}
        str1len = len(species)
        lab_names = list(set(lab_names))
        brain_region_names =  list(set(brain_region_names))
        neuron_subset_names = list(set(neuron_subset_names))

        for a in neuron_strings:

            str1 = a[:str1len]
            str1rest = a[str1len:]
            lab = max(list(filter(lambda x: str1rest.startswith(x), lab_names)), key=len)
            str2 = str1rest[len(lab):]
            region = max(list(filter(lambda x: str2.startswith(x), brain_region_names)), key=len)
            str3 = str2[len(region):]
            subset = max(list(filter(lambda x: str3.startswith(x), neuron_subset_names)), key=len)
            str4 = str3[len(subset):]
            #str_match = list(filter(lambda x: ))

    #        print(f"for \n{a}\n{species}{lab}{region}{subset}")
            new_filenames[a]= "_".join(f"{species}__{lab}__{region}__{subset}".split("/"))
        return new_filenames

    def get_neuromorpho_species_swc_files(self, dest_dir=None, include_signature=False, include_aux=True, species_index=None):
        """Given `species_index`, download zipped swc files of species, organized in 'lab:brain region:neuron type:swc files' hierarchy"""
        if dest_dir:
            dest_dir = f"{self.raw_data_dir}{dest_dir}"
        else:
            dest_dir = self.dest_directory
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            print(f"created new directory {dest_dir}")
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"created new directory {self.download_dir}")

        if not self.species:
            self.species = self.get_species(species_index)
            time.sleep(40)

        _, labs = self.get_species_source()
        while(len(labs)==0):
            time.sleep(5)
            _, labs = self.get_species_source()

        if (include_aux==True and not self.driver.find_element_by_name('Aux').is_selected()):
            self.driver.find_element_by_name('Aux').click()
            print("Clicked 'include aux files'")

        lab_names = [a.text for a in self.driver.find_elements_by_xpath("//font[@id='lvl2']")]

        brain_region_names =  [a.text for a in self.driver.find_elements_by_xpath("//font[@id='lvl3']")]

        neuron_subset_names = [a.text for a in self.driver.find_elements_by_xpath("//font[@id='lvl4']")]

        neuron_subsets = self.driver.find_elements_by_xpath("//font[@id='lvl4']/input")
        neuron_strings = [a.get_attribute('value') for a in  neuron_subsets]

        self.filenames_post = self.process_filenames("drosophila melanogaster",neuron_strings,lab_names,brain_region_names,neuron_subset_names)

        for i,a in enumerate(neuron_subsets):
            filename = self.filenames_post[neuron_strings[i]]
            if f"{filename}.zip" not in os.listdir(dest_dir):
                print("{} - Clicking on {}".format(i,neuron_strings[i]))
                a.click()
                self.driver.find_element_by_xpath("//input[@value='Get SWC files of selected neurons']").click()
                time.sleep(5)
                self.driver.switch_to.window(self.driver.window_handles[1])
                time.sleep(5)
                self.click_download_and_rename_when_finished(dest_dir=dest_dir, filename=filename)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                a.click()
            else:
                print(f"{filename} already in {dest_dir}")


        # for i,a in enumerate(labs):
        #     self.driver.switch_to.window(self.driver.window_handles[0])
        #     lab_name = lab_names[i]
        #     neuron_category_names, neuron_categories = self.get_neuron_category(a)
        #     for j,b in enumerate(neuron_categories):
        #         neuron_category_name = neuron_category_names[j]
        #         neuron_subcategory_names, neuron_subcategories = self.get_neuron_subcategory(b)
        #
        #         for k,c in enumerate(neuron_subcategories):
        #             neuron_subcategory_name = neuron_subcategory_names[k]
        #             print("{} - Clicking on {}".format(i,c.get_attribute("value")))
        #             c.click()
        #             self.driver.find_element_by_xpath("//input[@value='Get SWC files of selected neurons']").click()
        #             time.sleep(3)
        #             filename = f"{lab_name}__{neuron_category_name}__{neuron_subcategory_name}"
        #             print(filename)
        #             self.driver.switch_to.window(self.driver.window_handles[1])
        #             time.sleep(10)
        #             self.click_download_and_rename_when_finished(dest_dir=dest_dir, filename=filename)
        #             self.driver.close()
        #             self.driver.switch_to.window(self.driver.window_handles[0])
        #             c.click()

    def get_data_hierarchy(self, species_index=None):
        """Get hierarchy structure of data for given species"""
        self.get_species(species_index)

        time.sleep(40)
        try:
            species = self.driver.find_element_by_xpath("//font[@id='lvl1']").get_attribute('value')
        except selenium.common.exceptions.NoSuchElementException:
            print("Selenum error:",sys.exc_info()[0])
        except Exception as e:
            print(type(e))
            print("error:",sys.exc_info())
        print(species)
        names = []
        lab_names, labs = self.get_species_source()

        for i,a in enumerate(labs):
            cat_names, cats = self.get_neuron_category(a)

            for j,b in enumerate(cats):
                subcat_names, subcats = self.get_neuron_subcategory(b)
                for k,c in enumerate(subcats):
                    names.append((lab_names[i],cat_names[j],subcat_names[k]))
        return names

#====================================================================
# Other functions for data
#====================================================================

class ExtractData(object):
    def __init__(self, species):
        self.species = species
        self.error_files = []
    @staticmethod
    def get_zipped_data(zfile_path, filename=None, string="CNG version"):
        """
        Extract .swc data from .zip files in zfile_path and save in .h5 file

        Parameters
        ----------
        zfile_path : str
            path for .zip file
        filename : str
            name of zipped file to be pulled from archive
        string : string
            directory in archive from which to pull file
        """
        h5_filepath = f"{PROJECT_ROOT}/data/{SPECIES}.h5"
        if not os.path.exists(h5_filepath):
            h5py.File(h5_filepath,"w")

        archive = zipfile.ZipFile(zfile_path)
        files_w_errors = []
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

                with h5py.File(h5_filepath, 'a') as h5f:
                    h5f.create_dataset(f"{labname}/{cellname}/pbcode", data=data)
            except Exception as e:
                print(f"Error in {b.filename}\n\t{e}")
                files_w_errors.append(b.filename)
        self.error_files.extend(files_w_errors)

    @staticmethod
    def get_files_from_zipped_archive(file_dict):
        pass


    def generate_swc_file_buffer(self, error_dict):
        for a in error_dict:
                if error_dict[a]:
                    archive = zipfile.ZipFile(PROJECT_ROOT+"raw/data/swc_data/"+error_dict[a])
                    for b in filter(lambda x: ("CNG version" in x.filename) and (a in x.filename),  archive.filelist):
                        yield (b.filename,archive.read(b))
                else:
                    self.error_files.append(a)

    def get_missing_data(self,h5_filepath):
        all_neuron_ids = []

        with open(PROJECT_ROOT+"data/drosophila melanogaster__ids.tsv", 'r') as f:
            for row in reader(f):
                all_neuron_ids.append(row[0].split("\t")[1])
        neuronsw_pb = []
        if not os.path.exists(h5_filepath):
            h5py.File(h5_filepath,"w")

        with h5py.File(h5_filepath,'r+') as h5file:
            for a in list(h5file.keys()):
                neuronsw_pb.extend(list(h5file[a].keys()))
        error_neurons = set(all_neuron_ids) - set(neuronsw_pb)
        print(f"Total number of neuron_ids is {len(all_neuron_ids)}")
        print(f"Number of neurons with persistence barcode data in h5 file is {len(neuronsw_pb)}")
        print(f"Neurons without persistence barcode data is {len(error_neurons)}")

        error_neurons = list(error_neurons)

        neuron_dict = {}
        with open(PROJECT_ROOT+"data/drosophila melanogaster__ids.tsv", 'r') as f:
            next(f)
            for r in reader(f, delimiter="\t"):
                neuron_dict[r[1]]= [r[2],r[3],r[4]]

        zipfile_names = os.listdir(PROJECT_ROOT+"raw/data/swc_data/")

        swcfile_list = []
        for a in zipfile_names:
            swcfile_list.append((a, zipfiles.get_zipped_data(f"{PROJECT_ROOT}raw//data/swc_data/{a}", string="CNG version")))


        error_dict = {}
        for a in error_neurons:

            for b in list(filter(lambda x: a in "".join(x[1]), swcfile_list)):
                error_dict[a] = b[0]


        errorswc_gen = self.generate_swc_file_buffer(error_dict)

        files_w_errors = []
        for a in errorswc_gen:
            print(a[0])
            try:
                ntree = swcfunctions.NTree(a[1])
                data = ntree.get_persistence_barcode()
                pathlist = a[0].split("/")
                labname = pathlist[0]
                cellname = pathlist[-1].split(".")[0]
                print(f"{labname}/{cellname}")

                with h5py.File(f"{PROJECT_ROOT}/data/{self.species}.h5", 'a') as h5f:
                    h5f.create_dataset(f"{labname}/{cellname}/pbcode", data=data)
            except Exception as e:
                print(f"Error in {a[0]}\n\t{e}")
                files_w_errors.append(a[0])
        self.errors = files_w_errors

if __name__ == '__main__':
    ExtractData(sys.argv[1]).get_missing_data("data/drosophila melanogaster.h5")
