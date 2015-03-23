#!/usr/bin/env python
# encoding: utf-8
import httplib
from urlparse import urljoin, urlparse, urlsplit
import urllib2
import re
from time import sleep
from random import randrange
from page import Page

class DomainScraper(object):
    
    def __init__(self, scrape_subdirs=True):
        """
        Initialize all the class variables used in the class
        All the variables are Initialized here for convenience and readability
        """
        self.visited_links = {}     # Pythons Dictionary is already a HashMap
        self.domain_links = []      # All links found in domain and subdomains
        self.external_links = []    # For now external links are discarded, but these should be taken into account as well
        self.video_links = {}
        self.root_url = ""          # Root URL for the crawled website
        self.domain = ""            # The domain of the website.. Used to find relevant subdomains
        self.is_https = False       
        self.scrape_subdirs = scrape_subdirs
        # The header is just to ensure the website thinks it is a browser visiting it
        self.headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'}
       
      


    def start_search(self, url, sleep_time=2):
        """
        Start the search through the entire domain given as a parameter
        """
        
        # Ensure the URL is in the correct format 
        if url.startswith("www."):
            url = self.append_http(url)
        elif url[:8] == "https://":
            self.is_https = True
        
        # Return if the given URL is not valid
        if not self.check_url_existance(url):
            print   "URL: %s does not exist" % url
            return 
        
        self.root_url = url
        self.extract_domain_info(url)
        self.visited_links[url] = 1
        self.find_links(url, sleep_time)

        return self.domain_links

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

    def check_domain_boundry(self, url):
        """
        Check if the url is within the base domain to ensure the scraper does not go to other websites
        To speed up the check, only the beginning of the url is checked
        :param url:
        :return: Boolean stating wether or not the url is within the root domain
        """
        if self.root_url in url[:len(self.root_url)]:
            return True
        elif self.scrape_subdirs:
            return self.check_if_subdomain(url)
        else:
            return False

    # TODO This method is not exactly pretty and could be improved.
    def check_if_subdomain(self, url):
        """
        Check to see if the URL is actaully a subdomain of the crawled website
        Right now there is surely a lot of edgecases it does not take into account
        """

        # Break if there is any unreasonable characters in the url  
        if "@" in url or "?" in url: 
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
        # If the URL is a subdomain, the domain created should be identical to the URL e.g. "www.blog.example.com"
        return full_domain in url[:len(full_domain)]


    def append_http(self, url):
        if self.is_https:
            url = "https://%s" % url
        else:
            url = "http://%s" % url
        return url
    
    
    def extract_domain_info(self, url):
        """
        Extract the domain name from the URL
        This information is used to check if a link is a subdomain of the crawled website
        """
        parts = url.split(".")
        
        self.domain = ""
        for part in parts[1:]:
            self.domain += ".%s" % part
    
    
    def find_links(self, url, sleep_time):
        """
        Recursive function used to find all links within a given domain
        The function finds all links on a given page, and calls itself on each of them
        It sleeps a certain amount of time before requesting the page to be nice to the owner
        """
        
        # If the URL is not within the proper domain, or invalid it returns 
        if not self.check_domain_boundry(url) or not self.check_url_existance(url): 
            return
    
        # Ensure the URL has the correct format
        if url[:4] == "www.":
            url = self.append_http(url)
        
        # Add the url to the array of links 
        self.domain_links.append(url)

        # Sleeps just to be nice to the owner
        sleep(randrange(1,sleep_time))

        try:
            page = Page(url, self.headers, self.root_url)
        except ValueError as page_not_found:
            # If ValueError is raised, not page could be scraped from the URL
            return
        
        if page.get_videos():
            print "Found video on page: %s" % url
        else:
            print "Page %s had no urls" % url   

        for link in page.get_links():
            if not self.visited_links.has_key(link):
                # Only add a link to the stack if it has not been visited before
                # Now that the link has been visited, add it to the HashMap
                self.visited_links[link] = 1
                try:   
                     self.find_links(link, sleep_time)
                except urllib2.HTTPError as error: # All Http errors are discarded
                     print "Link: %s encountered an error %s" % (link, error)

    def link_is_valid_url(self, url):
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
