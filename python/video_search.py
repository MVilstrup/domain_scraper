#!/usr/bin/env python
# encoding: utf-8
import urllib2
from bs4 import BeautifulSoup

class VideoSearch(object):

    def __init__(self, soup):
        """
        Initialize a scraper used to find all videos on a given page.
        """   
        self.videos = {}
        self.soup = soup


    def search_page(self):
        """
        Params:
                @page : beautiful soup page
                The page the in which to look for videos
        """
        return self._search_iframes()


    def _search_iframes(self):
        return self.soup.find("iframe") != None 
