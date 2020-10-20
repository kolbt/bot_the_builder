'''
Scrape urls from amazon based on items I want to search
generate text output with list of review page urls.
'''

from selectorlib import Extractor
import requests
import json
from time import sleep
import csv
from dateutil import parser as dateparser
import random
import csv

# The items I'll be scraping review data for
#train_items = ( 'office+chair',
#                'office+desk',
#                'kitchen+table',
#                'living+room+couch',
#                'end+table',
train_items = ( 'bed+frame',
                'crib',
                'bookcase',
                'coffee+table')
          
# The proxy list is not in the github (don't want anyone to have my credentials)
def get_proxy_data(column):
    f = open('../../proxylist.csv', "r")
    lines = f.readlines()
    result=[]
    for x in lines:
        result.append(x.split('\t')[column])
    f.close()
    return result
    
proxy_ip = get_proxy_data(0)
del proxy_ip[0]
port_http = get_proxy_data(1)
port_socks = get_proxy_data(2)
login = get_proxy_data(3)
password = get_proxy_data(4)

# Grab my proxy data
def get_proxy():
    # Pick a random proxy to use
    in_proxy_ip = random.choice(proxy_ip)
    user = login[1]
    passwd = password[1]
    passwd = passwd.rstrip()
    ip = in_proxy_ip
#    port = port_socks[1]
    port = port_http[1]
    # Assemble the url
    proxy_url = "http://" + user + ":" + passwd + "@" + ip + ":" + port + "/"
    return {
        "http": proxy_url,
        "https": proxy_url
    }

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
    },
    # Curl-ed from safari browser: functioning
    {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'www.amazon.com'
    },
    # From chrome and https://httpbin.org/headers
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Host": "www.amazon.com",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    },
    # From Firefox
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Host": "www.amazon.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0"
    },
    # From Opera
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Host": "www.amazon.com",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 OPR/71.0.3770.148"
    }
]

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('selectors_review.yml')

def scrape(url, counter):
    # If you want more you can loop through page numbers
    url = "https://www.amazon.com" + url.rstrip() + "&pageNumber=" + str(counter)
    headers = random.choice(headers_list)
    # Download the page using requests
    print("Downloading %s"%url)
    current_proxy = get_proxy()
    try:
        r = requests.get(url, headers=headers, proxies=current_proxy)
    except:
        print("Connection Refused")
        return None
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create
    return e.extract(r.text)

for i in train_items:
    print("")
    print(i)
    print("")
    # Get the text file from the appropriate subfolder
    text_urls = "./review_urls/" + i + "_review_page_urls.txt"
    output = i + "_review_data.csv"
    with open(text_urls,'r') as urllist, open(output,'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["title","content","date","variant","images","verified","author","rating","product","url"],quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for url in urllist.readlines():
            # We don't want redirected urls
            if "picassoRedirect" in url:
                continue
            last_page = 0
            for page_count in range(0, 100):
                data = scrape(url, page_count)
                if data:
                    # Break if no reviews on page
                    if data['reviews'] == None:
                        break
                    for r in data['reviews']:
                        r["product"] = data["product_title"]
                        r['url'] = url
                        if r['rating'] == None:
                            last_page = 1
                            continue
                        if 'verified' in r:
                            if r['verified'] == None:
                                r['verified'] = 'No'
                            elif 'Verified Purchase' in r['verified']:
                                r['verified'] = 'Yes'
                            else:
                                r['verified'] = 'Yes'
                        r['rating'] = r['rating'].split(' out of')[0]
                        date_posted = r['date'].split('on ')[-1]
                        if r['images']:
                            r['images'] = "\n".join(r['images'])
                        r['date'] = dateparser.parse(date_posted).strftime('%d %b %Y')
                        writer.writerow(r)
                # If you've hit the last page of reviews move on to the next url
                if last_page == 1:
                    break
                sleep(1)
