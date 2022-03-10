import requests
import requests_html
from bs4 import BeautifulSoup


class Tour():
    def __init__(self):
        self.date = str()
        self.departy_city = str()
        self.days = str()
        self.food = str()
        self.people = str()
        self.price = str()


class SearchFilterResult():
    def __init__(self):
        self.title = str()
        self.rating = str()
        self.region = str()
        self.tours: list[Tour] = []


def get_countries() -> dict:
    countries = dict()
    data = requests.get('https://ht.kz//findForm/getMainData').json()
    for key, country in data['countries'].items():
        countries[key] = {
            'code': country['code'],
            'name': country['name'],
            'regions': data['regions'].get(key, dict())
        }

    return countries


def get_depart_cities() -> dict:
    data = requests.get('https://ht.kz//findForm/getMainData').json()
    return data['data']


def parse_tour(html):
    soup = BeautifulSoup(html, 'lxml')
    print(soup.find(class_='tour-list-place'))


def parse_tours(search_filter) -> list[SearchFilterResult]:
    url = 'https://ht.kz/findtours'
    session = requests_html.HTMLSession()
    date = '.'.join(map(str, [search_filter['day'],
                              search_filter['month'],
                              search_filter['year']]))
    params = {
        'region': search_filter['region_id'],
        'country': search_filter['country_id'],
        'stars': 'any',
        'adult': search_filter['adult'],
        'child': search_filter.get('child', 0),
        'hotel': '',
        'childAges': search_filter.get('child_ages', ''),
        'search': '1',
        'groupResultByHotels': '1',
        'bank': '',
        'splitRooms': '1',
        'delta': '0',
        'departCity': search_filter['departy_city_id'],
        'nightsFrom': '1',
        'nightsTo': '14',
        'dateFrom': date,
    }
    response: requests_html.HTMLResponse = session.get(url, params=params)
    response.html.render(timeout=120, scrolldown=True, sleep=5)
    html = response.html.html
    soup = BeautifulSoup(html, 'lxml')
    result = []
    for index, tag in enumerate(soup.find_all('app-tour'), 1):
        search_obj = SearchFilterResult()
        search_obj.title = tag.find(class_='ng-hotel-name').text.strip()
        try:
            search_obj.rating = tag.find(class_='ng-hotel-rating').text.strip()
        except Exception:
            pass

        search_obj.region = tag.find(class_='ng-hotel-region').text.strip()
        result.append(search_obj)

    return result
