#!/usr/bin/env python
# encoding: utf-8
import re
from bs4 import BeautifulSoup
from scraper import Scraper
from urlparse import urljoin, urlparse, urlsplit

class Page(object):

    def __init__(self, url, headers, root_url, depth):
        """
        Page object used to store all the relevant information about the pages
        containing videos

        Params:
                @url : str          (The url for the page)
                
                @headers : str
                All the header information used to make the scraping less detectable
                for for the site owners

                @root_url : str     (The root url for the domain)

                @depth : int        (The depth of the page from the root url)

        Attributes:
                @videos : dictionary (string : value)
                The number of videos of each type found on the page

                @references : int 
                The amount of other pages that references this page

                @soup : Beatutiful soup page
                The page scraped from the url

                @links : array (str)
                All the links found on this page
        """
        self.url = url
        self.headers = headers
        self.root_url = root_url
        self.depth = depth
        self.videos = {}
        self.references = 1
        scraper = Scraper(self.headers)
        self.soup = scraper.scrape(url)
        # make sure that the scraper actually got a result
        if self.soup is None:
            raise ValueError("No page could be loaded from url: %s" % self.url)
                
        self.links = self._find_all_links()
        self.find_videos()

    def get_links(self):
        """
        Returns all the found links on the current page 
        
        Returns:
                @links : array (str)
        """
        return self.links
    
    def contains_videos(self):
        """
        returns whether or not there is found any videos on the page

        Returns: 
                @ bool
        """
        return len(self.videos) != 0

    def find_videos(self):
        """
        Find all the videos on the page. This method is still very simple and needs
        to be more thorough in its search for videos. 
        """
        # TODO Make sure that iframes are searched better since they might
        # contain something else than videos

        # Count the number of iframes
        number_of_iframes = len(self.soup.findAll("iframe"))
        if number_of_iframes > 0:
            self.videos["iframe"] = number_of_iframes
        
        # Count the number of video tags
        number_of_video_tags = len(self.soup.findAll("video"))
        if number_of_video_tags > 0:
            self.videos["video"] = number_of_video_tags


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
            link = self._correct_link_syntax(link)
            if link is not None and self._link_is_valid_url(link):
                links.append(link)
        
        return links

    def _correct_link_syntax(self, link):
        """
        Simple method used to alter links into fully functional URLs and
        clean them in the process
        """
        
        # If the link is just one character long it is a reference to the root
        if len(link) <= 1:
            return self.root_url 

        # If the link ends with pdf or zip, the crawler 
        # should not attempt to dowload it, 
        # since this can take an extremely long time 
        if link.endswith("pdf") or link.endswith("zip"):
            return None

        
        # If the URL contains the text "return_url=" it 
        # can reach a non terminating loop
        if "return_url=" in link:
            return None
        
        # If the url contains a hashtag it is a reference to a part of the page, 
        # so the page is returned instead of the reference
        if "#" in link:
            base_link = urlsplit(link)
            if not "#" in base_link.geturl():
                link = base_link.geturl()
            else:
                return None
        
        # remove trailing slashes
        if link.endswith("/"):
            link = link[:-1]

        # If none of the above applies, we use the urljoin to create a proper url
        # If the link is actaully another domain, this domain is returned
        # otherwise the link is joined to the base to create a fully functional URL 
        return urljoin(self.root_url, link)
    
    def _link_is_valid_url(self, url):
        """
        Check if a URL is valid or not
        This method is taken from the Django Framework
        """
        regex = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url is not None and regex.search(url)

