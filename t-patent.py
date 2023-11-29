# ~ Import packages ~ #
from google_patent_scraper import scraper_class
import json

# ~ Initialize scraper class ~ #
scraper=scraper_class() 

# ~~ Scrape patents individually ~~ #
patent_1 = 'CN106144987A' #'US2668287A'

err_1, soup_1, url_1 = scraper.request_single_patent(patent_1)

# ~ Parse results of scrape ~ #
patent_1_parsed = scraper.get_scraped_data(soup_1,patent_1,url_1)

from pprint import pprint
pprint(patent_1_parsed)

for inventor in json.loads(patent_1_parsed['inventor_name']):
    print('Patent inventor : {0}'.format(inventor['inventor_name']))

