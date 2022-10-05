import requests
from bs4 import BeautifulSoup
import pandas as pd

# todo make it into function that takkes in format for URL

months = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'	}

URL = 'https://www.mtgtop8.com/format?f=MO'
page = requests.get(URL)
website_link = 'https://www.mtgtop8.com/'

#get_tier_list_links()

soup = BeautifulSoup(page.content, "html.parser")

d2b_element = soup.find(attrs={"name": "archive_d2b"})  # search for <eslect> tag
d2b_options = d2b_element.find_all(name='option')  # get all <option>s from <select>

month_link = []
month = []
year = []

for element in d2b_options:
    if "The Decks to Beat" in element.text:
        month_link.append(element['value'])  # link to decks of that month
        text = element.text
        text = text[text.index('-') + 2:]
        text = text.replace('\'', '20')
        split_text = text.split()
        month_name = (split_text[0])
        for key, value in months.items():
            if value == month_name:
                month.append(key)
                break
        year.append(split_text[1])

decks_to_beat_months = pd.DataFrame(columns=['Month', 'Year', 'Link to month'])
decks_to_beat_months['Month'] = month
decks_to_beat_months['Year'] = year
decks_to_beat_months['Link to month'] = month_link
decks_to_beat_months['Link to month'] = website_link + decks_to_beat_months['Link to month']

print(decks_to_beat_months)

