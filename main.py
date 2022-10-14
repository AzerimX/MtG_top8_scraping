import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

supported_formats = {
    'standard': 'format?f=ST',
    'pioneer': 'format?f=PI',
    'modern': 'format?f=MO',
    'legacy': 'format?f=LE',
    'historic': 'format?f=HI',
    'vintage': 'format?f=VI',  # low ammount of data
    'pauper': 'format?f=PAU'  # literally 1 tier list, moatly for test purposes
}

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
    12: 'December'
}

url = 'https://www.mtgtop8.com/'

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.width = 0


def get_tier_list_links(mtg_format: str) -> pd.DataFrame:
    """
    Takes format name, return Pandas DataFrame with link to tier list for each month that is available on mtgtop8.com
    :param str mtg_format: one of the supported formats
    :return: pd.DataDrame with links to each tier list
    """

    mtg_format = mtg_format.lower()  # make input lower case
    if mtg_format in supported_formats:
        format_url = supported_formats[mtg_format]
    else:
        raise Exception('Format not on the list of formats: ', mtg_format)

    full_url = url + format_url
    time.sleep(random.randint(0, 3))
    page = requests.get(full_url)  # get the page
    soup = BeautifulSoup(page.content, "html.parser")  # get only it's content
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
    decks_to_beat_months['Link to month'] = url + decks_to_beat_months['Link to month']
    # decks_to_beat_months = decks_to_beat_months.iloc[::-1]  # reverse order of elements in DataFrame
    # print(decks_to_beat_months)
    return decks_to_beat_months


def get_deck_links_month(tier_list_url: str) -> pd.DataFrame:
    """
    Given a URL for a tier list scrapes all deck links in that tier list
    :param str tier_list_url: string that is a link to a tier list
    :return: pd.DataFrame with links to all decks on that page
    """
    time.sleep(random.randint(0, 3))
    page = requests.get(tier_list_url)  # get the page
    soup = BeautifulSoup(page.content, "html.parser")  # get only it's content
    # this is spaghetti but the website is also spaghetti
    searching_by_style = soup.find_all(style='margin:0px 4px 0px 4px;')
    decks = []
    for element in searching_by_style:  # it should be exactly 1 iteration any ways
        trs = element.find_all('tr')
        for index, tr in enumerate(trs):
            tier = index + 1
            # print('Tier ' + str(tier))
            aas = all_links = tr.find_all('a')  # Find all links
            deck_name = ""
            deck_link = ""
            x = iter(aas)
            if len(aas) % 3 != 0:
                raise Exception("Number of links isn't devideable by zero (something went wrong!)")
            for a_1, a_2, a_3 in zip(x, x, x):
                try:
                    deck_name = a_2.contents[0]
                    deck_link = a_2['href']
                    deck_author = a_3.contents[0]
                    # print(tier, deck_name, deck_link, deck_author)
                    full_deck_link = url + 'event' + deck_link
                    decks.append([tier, deck_name.strip(), full_deck_link, deck_author.strip()])
                except IndexError:
                    print('Likely no deck link and author, only picture!')
                    print(a_1, a_2, a_3)

    decks_df = pd.DataFrame(decks, columns=['Tier', 'Name', 'Deck link', 'Author name'])
    return decks_df


def get_deck_links_all(mtg_format: str) -> pd.DataFrame:
    """
    Get all decks from "decks to beat" for a given format.
    :param str mtg_format: one of the supported formats
    :return: pd.DataFrame with the month, tier, link to the deck and other data
    """

    mtg_format = mtg_format.lower()  # make input lower case
    if mtg_format not in supported_formats:
        raise Exception('Format not on the list of formats: ', mtg_format)

    tier_lists = get_tier_list_links(mtg_format)
    all_decks_from_format = pd.DataFrame(columns=
                                         ['Year', 'Month', 'Tier', 'Name', 'Author name', 'Deck link'])
    year = []
    month = []
    tier = []
    name = []
    author_name = []
    deck_link = []
    for index, row in tier_lists.iterrows():
        deck_from_month = get_deck_links_month(row['Link to month'])
        print('Adding', ': ', row['Month'], '.', row['Year'], sep='')
        for index2, row2 in deck_from_month.iterrows():
            year.append(row['Year'])
            month.append(row['Month'])
            tier.append(row2['Tier'])
            name.append(row2['Name'])
            author_name.append(row2['Author name'])
            deck_link.append(row2['Deck link'])

    all_decks_from_format['Year'] = year
    all_decks_from_format['Month'] = month
    all_decks_from_format['Tier'] = tier
    all_decks_from_format['Name'] = name
    all_decks_from_format['Author name'] = author_name
    all_decks_from_format['Deck link'] = deck_link

    return all_decks_from_format


def get_deck_list(deck_link: str) -> str:
    """
    Scrape deck list from provided deck link
    :param str deck_link: deck link to mtgtop8.com
    :return: deck list as string
    """

    time.sleep(random.randint(0, 3))
    page = requests.get(deck_link)
    soup = BeautifulSoup(page.content, "html.parser")  # get only it's content
    found_element = soup.find_all('a', {'href': re.compile(r'mtgo')})
    if len(found_element) != 1:
        raise Exception('No MTGO deck link or other links containing string "mtgo"')
    mtgo_url = found_element[0]['href']
    full_url = url + mtgo_url
    # print(full_url)
    time.sleep(random.randint(0, 3))
    page = requests.get(full_url)  # get the *.txt file on the website containing deck list in MTGO format
    deck_list = page.text
    return deck_list


def get_all_decklists(mtg_format: str) -> pd.DataFrame:
    """
    Given a format returns a DataFrame with information about all decks, including deck lists
    :param str mtg_format: one of the supported formats
    :return: pd.Dataframe with deck lists and other information
    """

    deck_strings = []
    all_deck_lists = get_deck_links_all(mtg_format)
    print("\nTotal decklists found:", len(all_deck_lists))
    for index, row in all_deck_lists.iterrows():
        deck_list = get_deck_list(row['Deck link'])  # get the decklist to string format from its web page
        # noinspection PyTypeChecker
        print("%s. Added deck list for %s (%s.%s)" % (str(index+1), row['Name'], row['Month'], row['Year']))
        deck_strings.append(deck_list)

    all_deck_lists['Deck list'] = deck_strings
    print(all_deck_lists)

    return all_deck_lists


# get_deck_list('https://www.mtgtop8.com/event?e=38037&d=484549&f=MO')
format_to_scrape = 'modern'
# print(get_deck_links_all(format_to_scrape))
df_to_save = get_all_decklists(format_to_scrape)
df_to_save.to_csv(path_or_buf=str(format_to_scrape + " decks.csv"), index=False)



