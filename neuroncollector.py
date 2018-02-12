'''
Scrape websites using Firefox or PhantomJS.  Store in predetermined location (directory or mongo database)
'''
import time
import pymongo
#from urllib import urlencode
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

MONGODB_URI = 'mongodb://localhost:27017/'
MONGODB_NAME = 'aibs'

class Scraper(object):
    """

    """
    def __init__(self,
                 dbname=MONGODB_NAME,
                 browser="Firefox"):
        # connect to
        try:
            self.mongoclient = pymongo.MongoClient(MONGODB_URI)
            print("Connected to {}".format(MONGODB_URI))
        except pymongo.errors.ConnectionFailure as e:
            print("Could not connect to MongoDB: %s".format(e))
        self.mongodbase = self.mongoclient[dbname]
        self.coll = self.mongodbase['members']
        self.browser = browser
        if self.browser == "Firefox":
            self.use_firefox()
        elif self.browser == "Phantom":
            self.use_phantom()

    def use_firefox(self):
        self.driver = webdriver.Firefox(firefox_binary=FirefoxBinary(
            firefox_path='/usr/bin/firefox'))

    def use_phantom(self):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        # settings to emulate my machine, which works
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML,\
            like Gecko) Chrome/56.0.2924.76 Safari/537.36/")
#        self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
        self.driver = webdriver.PhantomJS(executable_path='/usr/local/share/phantomjs-1.9.7-linux-x86_64/bin/phantomjs',desired_capabilities=dcap)
#        self.driver.implicity_wait(5)
        self.driver.set_window_size(839, 937)