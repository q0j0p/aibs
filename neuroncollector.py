'''
Scrape websites using Firefox or PhantomJS
'''
import time
from urllib import urlencode
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class Scraper(object):
    """
    Simple scraper for the allrecipes.com website.


    """
    def __init__(self,
                 base_url=BASE_URL,
                 dbname=MONGODB_NAME,
                 browser="Firefox"):

        self.base_url = base_url
        try:
            self.mongoclient = pymongo.MongoClient(MONGODB_URI)
            print "Connected to {}".format(MONGODB_URI)
        except pymongo.errors.ConnectionFailure as e:
            print "Could not connect to MongoDB: %s".format(e)
        self.mongodbase = self.mongoclient[dbname]
        self.members_coll = self.mongodbase['members']
        self.recipes_coll = self.mongodbase['recipes']
        self.browser = browser
        if self.browser == "Firefox":
            self.use_firefox()
        elif self.browser == "Phantom":
            self.use_phantom()

    def use_firefox(self):
        self.driver = webdriver.Firefox(firefox_binary=FirefoxBinary(
            firefox_path='/Applications/FirefoxESR.app/Contents/MacOS/firefox'))

    def use_phantom(self):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        # settings to emulate my machine, which works
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML,\
            like Gecko) Chrome/56.0.2924.76 Safari/537.36/")
#        self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
        self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
        self.driver.implicity_wait(10)
        self.driver.set_window_size(839, 937)
