import argparse
import os
from PageScraper import DomainScraper
from page import Page
from visualize.bar_chart import BarChart
ap = argparse.ArgumentParser()
ap.add_argument("-u", "--url", required=True, help="The base URl of the website you want to scrape ")
ap.add_argument("-o", "--output", required=True, help="The name of the csv file that should be saved")
args = vars(ap.parse_args())

directory = os.path.dirname(os.path.realpath(__file__))

file_name = "%s/%s.csv" % (directory, args["output"])

csv = open(file_name, "w")

# Start the domain scraper and give it a base domain to scrape from
scraper = DomainScraper()
video_pages = scraper.start_search(args["url"])

urls = []
references = []
depths = []


csv_text = "url, refrences, depths, iframes, videos\n"
for url, page in video_pages.iteritems():
    urls.append(url)
    references.append(page.references)
    depths.append(page.depth)
    videos = 0
    iframes = 0
    for name, videos in page.videos.iteritems():
        if name == "iframe":
            iframes += videos 
        elif name == "video":
            videos += videos
    csv_text += "%s,%s,%s,%s,%s\n" % (url, page.references, page.depth, iframes, videos)

csv.write(csv_text)

bar_chart = BarChart(bar_groups=urls)
bar_chart.add_data(references, label="References")
bar_chart.show()

bar_chart = BarChart(bar_groups=urls)
bar_chart.add_data(depths, label="Depths")
bar_chart.show()

