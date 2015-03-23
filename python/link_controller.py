#!/usr/bin/env python
# encoding: utf-8
import httplib
from urlparse import urljoin, urlparse, urlsplit
import urllib2
import re

class LinkController(object):

    def __init__(self, root_url):
        
        # Return if the given URL is not valid
        if not self.check_url_existance(root_url):
            raise ValueError("URL: %s does not exist" % root_url)
       
        self.root_url = root_url
        self.domain = self.extract_domain(root_url)    

    def get_server_status_code(self, url):
        """
        Download just the header of a URL and
        return the server's status code.
        http://pythonadventures.wordpress.com/2010/10/17/check-if-url-exists/
        """
        # http://stackoverflow.com/questions/1140661
        host, path = urlparse(url)[1:3]  # elems [1] and [2]
        try:
            conn = httplib.HTTPConnection(host)
            conn.request('HEAD', path)
            return conn.getresponse().status
        except StandardError:
            return None
        except httplib.BadStatusLine:
            return None

    def check_url_existance(self, url):
        """
        Check if a URL exists without downloading the whole file.
        We only check the URL header.
        http://pythonadventures.wordpress.com/2010/10/17/check-if-url-exists/
        """
        # see also http://stackoverflow.com/questions/2924422
        good_codes = [httplib.OK, httplib.FOUND, httplib.MOVED_PERMANENTLY]
        return self.get_server_status_code(url) in good_codes

    def check_domain_boundry(self, url, scrape_subdirs=True):
        """
        Check if the url is within the base domain 
        to ensure the scraper does not go to other websites
        To speed up the check, only the beginning of the url is checked
        Params: 
                @url : str  
        
        Returns: 
                @Boolean stating wether or not the url is within the root domain
        """
        if self.root_url in url[:len(self.root_url)]:
            return True
        elif scrape_subdirs:
            return self.check_if_subdomain(url)
        else:
            return False

    # TODO This method is not exactly pretty and could be improved.
    def check_if_subdomain(self, url):
        """
        Check to see if the URL is actaully a subdomain 
        of the crawled website. 
        
        Right now there is surely a lot of 
        edgecases it does not take into account
        """

        # Break if there is any unreasonable characters in the url  
        if "@" in url in url: 
            return False
        
        # Ensure the URL are in the correct format
        url = urljoin(self.root_url, url)
        
        # Locate the subdomain in the URL
        sub_domain = "";
        parts = url.split(".")
        if "www" in parts[0]:
            sub_domain = "%s.%s" % (parts[0], parts[1])
        else:
            sub_domain = parts[0]
        
        full_domain = "%s%s" % (sub_domain, self.domain) 
        
        # Return wether or not the URL is actually a subdomain of the crawled website 
        # If the URL is a subdomain, the domain created should 
        # be identical to the URL e.g. "www.blog.example.com"
        return full_domain in url[:len(full_domain)]
    
    def extract_domain(self, url):
        """
        Extract the domain name from the URL
        This information is used to check if a link is a 
        subdomain of the crawled website
        """
        parts = url.split(".")
        
        domain = ""
        for part in parts[1:]:
            domain += ".%s" % part
        
        return domain
