'''
Scrape urls from amazon based on items I want to search
generate text output with list of review page urls.
'''

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import csv
import random
from collections import OrderedDict

# The items I'll be scraping review data for
train_items = ( 'office+chair',
                'office+desk',
                'kitchen+table',
                'living+room+couch',
                'end+table',
                'bed+frame',
                'crib',
                'bookcase',
                'coffee+table')

# This data was created by using the curl method explained above
headers_list = [
    # Firefox 77 Mac
     {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    # Firefox 77 Windows
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    # Chrome 83 Mac
    {
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
    },
    # Chrome 83 Windows
    {
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    }
]

# Create ordered dict from Headers above
ordered_headers_list = []
for headers in headers_list:
    h = OrderedDict()
    for header,value in headers.items():
        h[header]=value
    ordered_headers_list.append(h)

# This driver should allow javascript to load
#driver = webdriver.PhantomJS()
        
def request_page(in_url, prefix="https://www.amazon.com/s?k=", suffix="&ref=nb_sb_noss"):
    '''This will request whatever page I feed in takes in prefix and suffix to url'''
    url = prefix + in_url + suffix
    # For javascript if needed
#    driver.get(my_url)
    # Spoof the user agent
    header = random.choice(headers_list)
    r = requests.Session()
    r.headers = header
    page = r.get(url)
    if page.status_code == 200:
        return page
    else:
        return "Error! Page status exit code {}".format(page.status_code)
       
# Product url
item_urls = []
# Link to reviews page
review_urls = []
# Text of each review
reviews = []

# Let's loop through our search items
for i in range(len(train_items)):

    # What item am I scraping for
    print("")
    print(train_items[i])

    # Distinct list for each search item
    item_urls.append([])
    review_urls.append([])
    reviews.append([])
    
    # Get page content of product search
    response = request_page(train_items[i])
 
    # This will just tell me if I was denied access
    print(f'Response for general search: {response}\n')
    # Instantiate beautifulsoup on the search page
    soup = BeautifulSoup(response.content, "lxml")
    
    # This grabs the product urls
    divs = soup.find_all("a", attrs={"class": "a-size-base a-link-normal a-text-normal"})
    for j in divs:
        item_urls[i].append(j.get("href"))
        
#    # Get all my product pages in a text file
#    product_urls_text = train_items[i] + '_product_page_urls.txt'
#    z = open(product_urls_text, 'w')
#    for j in range(len(item_urls[i])):
#        z.write(item_urls[i][j] + '\n')
#    z.close()
    
    # Check to make sure we are getting good urls
#    print(item_urls[i][-1])

    # Get all my product pages in a text file
    product_urls_text = train_items[i] + '_product_page_urls.txt'
    z = open(product_urls_text, 'w')
    # Go through product pages, get review page urls
    for j in range(len(item_urls[i])):
        response = request_page(item_urls[i][j], prefix="https://www.amazon.com", suffix="")
        if response != "Error! Page status exit code 404":
            print(f'Response for {item_urls[i][j]}: {response}')
            soup = BeautifulSoup(response.content, "lxml")
            for k in soup.find_all("a",{'data-hook':"see-all-reviews-link-foot"}):
                if k['href'] not in review_urls[i]:
                    review_urls[i].append(k['href'])
                    z.write(item_urls[i][j] + '\n')
    z.close()

    # At this point I'm going to make a text file that has all my product urls in it
    review_urls_text = train_items[i] + '_review_page_urls.txt'
    g = open(review_urls_text, 'w')
    for j in range(len(review_urls[i])):
        g.write(review_urls[i][j] + '\n')
    g.close()
    # Check to make sure we are getting good review urls
#    print(review_urls[i][-1])
