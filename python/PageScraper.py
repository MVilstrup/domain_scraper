#!/usr/bin/env python
# encoding: utf-8
import re
from time import sleep
from random import randrange
from page import Page
from link_controller import LinkController

class DomainScraper(object):
    
    def __init__(self,root_url, scrape_subdirs=True):
        """
        Initialize all the class variables used in the class
        All the variables are Initialized here for convenience and readability
        """
        self.visited_links = {}     # Pythons Dictionary is already a HashMap
        self.domain_links = {}      # All links found in domain and subdomains
        self.video_links = {}       # All pages containing videos on them
        self.is_https = False       
        
        
        # Ensure the URL is in the correct format 
        if root_url.startswith("www."):
            root_url = self.append_http(root_url)
        elif root_url[:8] == "https://":
            self.is_https = True
        
        self.root_url = root_url
        self.link_controller = LinkController(root_url)

        # The header is just to ensure the website thinks it is a browser visiting it
        self.headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'}

    def start_search(self, sleep_time=2):
        """
        Start the search through the entire domain given as a parameter
        """
        
        self.visited_links[self.root_url] = 1
        self.find_links(self.root_url, sleep_time, depth=0)

        return self.video_links

    def append_http(self, url):
        if self.is_https:
            url = "https://%s" % url
        else:
            url = "http://%s" % url
        return url
    
    def find_links(self, url, sleep_time, depth):
        """
        Recursive function used to find all links within a given domain
        The function finds all links on a given page, and calls itself on each of them
        It sleeps a certain amount of time before requesting the page to be nice to the owner
        """
        
        # If the URL is not within the proper domain 
        if not self.link_controller.check_domain_boundry(url):
            return
        
        # If the link is invalid there is no reason to follow it
        if not self.link_controller.check_url_existance(url): 
            return
    
        # Ensure the URL has the correct format
        if url[:4] == "www.":
            url = self.append_http(url)
        
        # Add the url to the array of links 
        self.domain_links[url] = 1

        # Sleeps just to be nice to the owner
        sleep(randrange(1,sleep_time))

        try:
            page = Page(url, self.headers, self.root_url, depth=depth)
        except ValueError as page_not_found:
            # If ValueError is raised, page could not be scraped from the URL
            return
        
        if page.contains_videos():
            print "Found video on page %s" % url 
            self.video_links[url] = page
        
        new_depth = depth + 1

        for link in page.get_links():
            if not self.visited_links.has_key(link):
                # Only add a link to the stack if it has not been visited before
                # Now that the link has been visited, add it to the HashMap
                self.visited_links[link] = 1
                try:   
                     self.find_links(link, sleep_time, new_depth)
                except urllib2.HTTPError as error: # All Http errors are discarded
                     print "Link: %s encountered an error %s" % (link, error)
            else:
                # Add a reference and check to see if the current depth 
                # is smaller than the link of a stored video page, 
                # and update its depth to find the shortest
                # path to a page containing a video
                if self.video_links.has_key(link):
                    visited_page = self.video_links[link]
                    visited_page.references += 1
                    if new_depth < visited_page.depth:
                        visited_page.depth = new_depth

