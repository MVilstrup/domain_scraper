import urllib2
from bs4 import BeautifulSoup

class Scraper():

    def __init__(self, headers):
        self.headers = headers

    def scrape(self, url):
        try:
            req = urllib2.Request(url, headers=self.headers)
            return  BeautifulSoup(urllib2.urlopen(req).read())
        except urllib2.URLError:
            print "connection Timed out"
            return None
