
import time
import pymongo
import os
import matplotlib.pyplot as plt
import matplotlib.image as mplimg
#from urllib import urlencode
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

PROJECT_NAME = 'aibs'
MONGODB_URI = 'mongodb://localhost:27017/'
MONGODB_NAME = 'aibs'
MACHINE_OPTIONS= ['mac', 'ubuntu']

class NeuroScraper(object):

    """Web scraping functions for data collection.

    """

    def __init__(self,
                 dbname=MONGODB_NAME,
                 browser="Firefox",
                 machine="mac",
                 url="http://neuromorpho.org/byspecies.jsp"):
        # connect to
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
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('browser.download.folderList', 2) # custom location
        self.profile.set_preference('browser.download.manager.showWhenStarting', False)
        self.profile.set_preference('browser.download.dir', self.raw_data_dir)
        self.profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip')
        print(self.profile)
        if self.machine==MACHINE_OPTIONS[0]: # mac
            self.driver = webdriver.Firefox(firefox_binary=FirefoxBinary(
                firefox_path='/Applications/FirefoxESR.app/Contents/MacOS/firefox'), firefox_profile=self.profile)
        elif self.machine==MACHINE_OPTIONS[1]: # ubuntu
            os.system("Xvfb :10 -ac &")
            os.system("export DISPLAY=:10")
            self.driver = webdriver.Firefox(firefox_binary=FirefoxBinary(
                firefox_path='/usr/bin/firefox'), firefox_profile=self.profile)

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

    def close_driver(self):
        self.driver.close()

    """
    FYI: The following functions are neuromorpho.org-specific!
    """

    def get_species(self, species_index=None):
        """Get list of web elements corresponding to species on neuromorpho.org"""
        self.speciess = self.driver.find_elements_by_class_name("species")
        print("Total number of species:", len(self.speciess))
        species_names = [a.get_attribute("name") for a in self.speciess]
        if species_index == None:
            print("Species names")
            for i,a in enumerate(species_names):
                print(i,a)
            species_index = int(input("Enter species index:"))
        print("clicking on {}".format(species_names[species_index]))
        self.speciess[species_index].click()

    def get_species_source(self, id='drosophila melanogaster_chkbox'):
        """Get list of web elements corresponding to data source (labs) under species"""
        labs = self.driver.find_elements_by_xpath("//input[@id='"+id+"']")
        print("Source names (count:{}):".format(len(labs)))
        for i,a in enumerate(labs):
            print(i,a.get_attribute("value"))
        return labs

    def get_neuron_category(self,lab):
        """Get neuron category under data source (lab)"""
        lab_id = lab.get_attribute("value")
        neuron_categories =  self.driver.find_elements_by_xpath("//input[@id='"+lab_id+"_chkbox']")
        print([a.get_attribute("value") for a in neuron_categories])
        return neuron_categories

    def get_swc_files(self):
        self.driver.get(self.target_url)

    def get_neuromorpho_species_swc_files(self, include_signature=False, include_aux=True, species_index=None):
        self.get_page()
        self.get_species(species_index)
        time.sleep(30)
        labs = self.get_species_source()
        while(len(labs)==0):
            time.sleep(5)
            labs = self.get_species_source()

        if include_aux==True:
            self.driver.find_element_by_name('Aux').click()
            print("Clicked 'include aux files'")
        for i,a in enumerate(labs):
            self.driver.switch_to.window(self.driver.window_handles[0])
            neuron_categories = self.get_neuron_category(a)
            for j,b in enumerate(neuron_categories):
                print("{} - Clicking on {}".format(i,b.get_attribute("value")))
                b.click()
                self.driver.find_element_by_xpath("//input[@value='Get SWC files of selected neurons']").click()
                time.sleep(3)
                self.driver.switch_to.window(self.driver.window_handles[1])
                time.sleep(10)
                self.driver.find_element_by_name('yes').click()
                time.sleep(20)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                b.click()


class NMorpho(object):
    """"""
