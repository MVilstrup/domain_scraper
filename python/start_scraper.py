import argparse
import os
from PageScraper import DomainScraper

ap = argparse.ArgumentParser()
ap.add_argument("-u", "--url", required=True, help="The base URl of the website you want to scrape ")
args = vars(ap.parse_args())

directory = os.path.dirname(os.path.realpath(__file__))
file = args["url"].replace("http://", "")
file_name = "%s%s.csv" % (directory,file)

file = open(file_name, "w")


# Start the domain scraper and give it a base domain to scrape from
scraper = DomainScraper()
links = scraper.start_search(args["url"])

# When all links are found, write them to a file
for link in links:
    file.write(link)
