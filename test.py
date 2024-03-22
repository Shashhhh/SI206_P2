import requests
from bs4 import BeautifulSoup as bs
import re
import os
import csv
def goodreads_searcher(query): 
    lst = []
    response = requests.get(f'https://www.goodreads.com/search?q={query}&qid=')
    soup = bs(response.text, 'html.parser')
    table = soup.find('table', class_='tableList')
    if table:
        tablerows = table.find_all('tr', {'itemtype': 'http://schema.org/Book'})
        for row in tablerows:
            lst.append(row.find('span', {'itemprop': 'name'}).text)
    return lst

print(goodreads_searcher('airbnb'))