import requests_html
from bs4 import BeautifulSoup


def get_countries() -> dict[str, int]:
    countries = dict()
    session = requests_html.HTMLSession()
    response = session.get('https://ht.kz/')
    response.html.render(timeout=60)
    html = response.html.html
    soup = BeautifulSoup(html, 'lxml')
    for country_tag in soup.find(
        attrs={'class': 'clever-list-countries'}
    ).find_all(attrs={'data-value': True}):
        print(country_tag.get('data-value'), country_tag.text)
