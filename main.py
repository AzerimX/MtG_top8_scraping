import requests
from bs4 import BeautifulSoup
import pandas as pd

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


def get_tier_list_links(mtg_format: str) -> pd.DataFrame:
    """
    Takes format name, return Pandas DataFrame with link to tier list for each month that is available on mtgtop8.com
    Supported formats:
    - Standard
    - Pioneer
    - Modern
    - Legacy
    - Historic
    """

    formats = {
        'standard': 'format?f=ST',
        'pioneer': 'format?f=PI',
        'modern': 'format?f=MO',
        'legacy': 'format?f=LE',
        'historic': 'format?f=HI'
    }

    mtg_format = mtg_format.lower()  # make input lower case
    if mtg_format in formats:
        format_url = formats[mtg_format]
    else:
        raise Exception('Format not on the list of formats: ', mtg_format)

    full_url = url + format_url
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
    print(decks_to_beat_months)
    return decks_to_beat_months


def get_deck_links(tier_list_url: str) -> pd.DataFrame:
    """
    :param tier_list_url: string that is a link to a tier list
    :return: pd.DataFrame with links to all decks on that page
    """
    page = requests.get(tier_list_url)  # get the page
    soup = BeautifulSoup(page.content, "html.parser")  # get only it's content
    # this is spaghetti but the website is also spaghetti
    searching_by_style = soup.find_all(style='margin:0px 4px 0px 4px;')
    #print(searching_by_style)
    for element in searching_by_style:  # it should be exactly 1 iteration any ways
        asdjjj = element.find_all('tr')
        # todo each <TR> is a tier on the tier list!
        print(asdjjj)
        # ahref = element.find_all('a')
        # for element2 in ahref:
        #     print(element2)
    #asd = soup.find_all(attrs={'class': 'S14'})  # spaghetti but the website is also a pasta
    #print(asd)


modern_tier_lists = get_tier_list_links('modern')
get_deck_links('https://www.mtgtop8.com/event?e=2552&f=MO')
# todo scrapping tier list
