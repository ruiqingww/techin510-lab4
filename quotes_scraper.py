import os
from tqdm.auto import tqdm
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from db import Database

def get_internal_description(page_link,a_url):
    BASE_URL = page_link.split('page-')[0]
    internal_url = BASE_URL + a_url

    response = requests.get(internal_url)
    # print(f"internal_url {internal_url}")
    
    if '404 Not Found' in response.text:
        print("Warning: page not found at {internal_url}")
        return ""
    soup = BeautifulSoup(response.text, 'html.parser')
    desc = soup.select_one('div#product_description.sub-header').find_next('p').text
    # print("quote_divs {}".format(quote_divs))
    # desc=quote_div.select_one('div#product_description.sub-header').find_next('p').text
    
    return desc

load_dotenv()
BASE_URL = 'https://books.toscrape.com/catalogue/page-{x}.html'
with Database(os.getenv('DATABASE_URL')) as pg:
    pg.create_table()

    # TODO: use argparse to enable truncating table
    #pg.truncate_table()

    quotes = []
    x = 1
    for i in tqdm(range(1, 100)):
        url = BASE_URL.format(x=x)
        print(f"Scraping {url}")
        response = requests.get(url)

        # if outside of valid page range
        if '404 Not Found' in response.text:
            print("Error: page not found")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # select all quote divs
        quote_divs = soup.select('li.col-xs-6.col-sm-4.col-md-3.col-lg-3')

        for quote_div in tqdm(quote_divs):
            # print("searching")
            # parse individual quote
            quote = {}
            quote['title'] = quote_div.select_one('h3').select_one('a')['title']
            try:
                quote['description'] = get_internal_description(url,quote_div.select_one('h3').select_one('a')['href'])
            except:
                quote['description'] = "No description available"
                print(f"No description available at {quote['title']}")
            quote['price'] = quote_div.select_one('p.price_color').text.split('£')[1]
            quote['rating'] = str(quote_div.find_all('p',class_='star-rating')[0]['class'][1])
            # print(quote)
            # quote['avail'] = quote_div.select_one('p.instock.availability').text
            #quote['author_link'] = quote_div.select('span')[1].select('a')[0]
            #quote['tags'] = ','.join([tag.text for tag in quote_div.select('a.tag')])
            #quote['tag_links'] = [tag['href'] for tag in quote_div.select('a.tag')]
            
            # insert into database
            pg.insert_quote(quote)
            quotes.append(quote)
        x += 1

    print(quotes)
    
