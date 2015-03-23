#!/usr/bin/env python
# encoding: utf-8

from bs4 import BeautifulSoup
from scraper import Scraper
from urlparse import urljoin, urlparse, urlsplit


class Page(object):

    def __init__(self, url, headers, root_url):
        self.url = url
        self.headers = headers
        self.root_url = root_url

        scraper = Scraper(self.headers)
        self.soup = scraper.scrape(url)
        # make sure that the scraper actually got a result
        if self.soup is None:
            raise ValueError("No page could be loaded from url: %s" % self.url)
        
        self.links = self._find_all_links()

    def get_links(self):
        return self.links
    
    def get_videos(self):
        return self.soup.find("iframe") != None

    def find_videos(self):
        pass

    def _find_all_links(self):
        """
        Method used to find all the urls on the page.
        It goes through all ankors on the page, checks to see if it has a href
        If this is the case, it cleans the link and returns all the links
        """
        links = []
        for a in self.soup.findAll("a"):
            link = ""
            try:
                link = a["href"]
            except KeyError:
                # Sometimes the ankors does not contain any href
                # In this case nothing should be done with it
                continue
            
            links.append(self._correct_link_syntax(link))
        
        return links

    def _correct_link_syntax(self, link):
        """
        Simple method used to alter links into fully functional URLs
        """
        
        # If the link is just one character long it is a reference to the root
        if len(link) <= 1:
            return self.root_url
        
        # If the URL contains the text "return_url=" it can reach a non terminating loop
        if "return_url=" in link:
            return self.root_url
        
        # If the url contains a hashtag it is a reference to a part of the page, 
        # so the page is returned instead of the reference
        if "#" in link:
            base_link = urlsplit(link)
            return base_link.geturl()

        # If the link ends with pdf or zip, the crawler should not attempt to dowload it, 
        # since this can take an extremely long time 
        if link.endswith("pdf") or link.endswith("zip"):
            return self.root_url 
        
        # If none of the above applies, we use the urljoin to create a proper url
        # If the link is actaully another domain, this domain is returned
        # otherwise the link is joined to the base to create a fully functional URL 
        return urljoin(self.root_url, link)
    
