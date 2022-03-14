from multiprocessing.sharedctypes import Value
import traceback
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
        self.rating_star = int()
        self.region = str()
        self.image_src = str()
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


async def parse_tours(search_filter) -> tuple[list[SearchFilterResult],
                                              requests_html.HTML]:
    url = 'https://ht.kz/findtours'
    session = requests_html.AsyncHTMLSession()
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
        'splitRooms': '0',
        'delta': '0',
        'departCity': search_filter['departy_city_id'],
        'nightsFrom': '1',
        'nightsTo': '14',
        'dateFrom': date,
    }
    response: requests_html.HTMLResponse = await session.get(url, params=params)
    script = '''$("button[class='ng-sort-btn']").eq(0).click()'''
    await response.html.arender(timeout=120, sleep=5, script=script)
    html = response.html.html
    soup = BeautifulSoup(html, 'lxml')
    result = []
    for tag in soup.find_all('app-tour'):
        search_obj = SearchFilterResult()
        search_obj.title = tag.find(class_='ng-hotel-name').text.strip()
        try:
            search_obj.rating = tag.find(class_='ng-hotel-rating').text.strip()
        except Exception:
            pass

        search_obj.rating_star = len(tag.find_all(src='/imgm/fb/icons/star.png'))
        search_obj.region = tag.find(class_='ng-hotel-region').text.strip()
        search_obj.image_src = tag.find('img').get('src')
        result.append(search_obj)

    await response.html.browser.close()
    return result, response.html


async def parse_tours_day(search_filter, index, day) -> list[Tour]:
    url = 'https://ht.kz/findtours'
    session = requests_html.AsyncHTMLSession()
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
        'splitRooms': '0',
        'delta': '0',
        'departCity': search_filter['departy_city_id'],
        'nightsFrom': '7',
        'nightsTo': '8',
        'dateFrom': date,
    }
    response: requests_html.HTMLResponse = await session.get(url, params=params)
    script = '''$("button[class='ng-sort-btn']").eq(0).click()'''
    await response.html.arender(timeout=120, sleep=5,
                                keep_page=True, script=script)
    result = search_filter['search_filter_result']
    data = result[index]
    soup = BeautifulSoup(response.html.html, 'lxml')
    for i, tag in enumerate(soup.find_all('app-tour')):
        title = tag.find(class_='ng-hotel-name').text.strip()
        if title == data.title:
            index = i
            break
            
    script = f'''
        $('button[class="ng-view-tours showHotelInfo"]').eq({index}).click();
    '''
    page = response.html.page
    await page.evaluate(script)
    await page.waitForSelector('.tour-list-place > div')
    for e in await page.querySelectorAll('button[class="nav-button btn-clear"]'):
        try:
            text = await page.evaluate('(element) => element.textContent', e)
            text = text.strip()
            days, _ = text.split()
            days = int(days)
            if days == day:
                await e.click()
                selector = f'b:contains("{text}")'
                for _ in range(30):
                    selector = f'''$("b:contains('{text}')").size()'''
                    await page.waitFor(1000)
                    if await page.evaluate(selector):
                        break

        except ValueError:
            continue
        except Exception:
            traceback.print_exc()

    script = '''
        () => {
            return $('.tour-list-place').html();
        }
    '''
    soup = BeautifulSoup(await page.evaluate(script), 'lxml')
    tours = []
    for tag in soup.find_all(attrs={'class': 'item-info'}):
        tour = Tour()
        for index, li_tag in enumerate(tag.find_all('li')):
            if index == 0:
                tour.date = li_tag.find('b').text.strip()
            elif index == 1:
                tour.departy_city = li_tag.find('b').text.strip()
            elif index == 2:
                tour.days = li_tag.find('b').text.strip()
            elif index == 3:
                tour.food = li_tag.find('b').text.strip()
            elif index == 4:
                tour.people = li_tag.find('span').text.strip()
            elif index == 5:
                tour.price = li_tag.find('b').text.strip()

        tours.append(tour)

    await response.html.browser.close()
    return tours
