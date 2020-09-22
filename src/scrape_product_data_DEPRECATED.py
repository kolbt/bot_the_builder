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

# Get a proxy list
def get_free_proxies():
    url = "https://free-proxy-list.net/"
    # get the HTTP response and construct soup object
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    proxies = []
    for row in soup.find("table", attrs={"id": "proxylisttable"}).find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    return proxies
    
proxies = get_free_proxies()
proxy = proxies[0]
print(proxy)

# The items I'll be scraping review data for
train_items = ( 'office+chair' , 'office+desk' )
#train_items = ( 'office+chair',
#                'office+desk',
#                'kitchen+table',
#                'living+room+couch',
#                'end+table',
#                'bed+frame',
#                'crib',
#                'bookcase',
#                'coffee+table')

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
        
def request_page(in_url, prefix="https://www.amazon.com", suffix=""):
    '''This will request whatever page I feed in takes in prefix and suffix to url'''
    url = prefix + in_url + suffix
    print(url)
    # Spoof the user agent
    header = random.choice(headers_list)
    r = requests.Session()
    r.headers = header
    page = r.get(url)
    if page.status_code == 200:
        return page
    else:
        return "Error! Page status exit code {}".format(page.status_code)


# Let's loop through our search items
for i in train_items:

    # Open the corresponding text file
    text_urls = "./product_urls/" + i + "_product_page_urls.txt"
    output = i + "_product_data.csv"
    with open(text_urls, 'r') as urllist, open(output, 'w') as outfile:
        # Write the headers for the csv
        writer = csv.DictWriter(outfile, fieldnames=["product", "ease_of_assembly", "sturdiness", "support", "comfort", "ergonomic"], quoting=csv.QUOTE_ALL)
        # Loop through each url in the product url file
        for url in urllist.readlines():
            # Scrape the page
            response = request_page(url)
            print(response)
            # Instantiate bs4
            soup = BeautifulSoup(response.content, "lxml")
            
            # Grab the product name
            for l in soup.find_all("span",{'id':"productTitle"}):
                print(l.text)
            
            # Ease of assembly
            divs = soup.find("div",{'id':"cr-summarization-attribute-attr-easy-to-assemble"})
            print(divs)
            for l in divs.find_all("span",{'class':"a-size-base a-color-tertiary"}):
                print(l.text)
            
            # Sturdiness
            
            # Support
            
            # Comfort
            
            # Ergonomic
