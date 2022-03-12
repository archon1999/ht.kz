import traceback
import asyncio
from collections import namedtuple

from pyppeteer.errors import ElementHandleError
import requests_html
from bs4 import BeautifulSoup


Option = namedtuple('Option', 'size price')
Category = namedtuple('Category', 'name parent_name url')
Product = namedtuple('Product', 'name category image_src code options')


async def get_categories() -> list[Category]:
    url = 'https://modkartina.ru/katalog-modulnyh-kartin'
    session = requests_html.AsyncHTMLSession()
    response = await session.get(url)
    html = response.html
    soup = BeautifulSoup(html.html, 'lxml')
    categories: list[Category] = []
    for category_tag in soup.find(id='column-left').li.ul.find_all('li'):
        parent_name = category_tag.a.text.strip()
        for child_tag in category_tag.find_all('li'):
            name = child_tag.text.strip('- \n')
            url = child_tag.find('a').get('href')
            category = Category(name, parent_name, url)
            categories.append(category)

    return categories


async def get_product(product_url, category):
    session = requests_html.AsyncHTMLSession()
    response = await session.get(product_url)
    html = response.html
    soup = BeautifulSoup(html.html, 'lxml')
    name = soup.find(attrs={'itemprop': 'name'}).text.strip()
    code = soup.find(attrs={'itemprop': 'model'}).text.strip()
    script = '''
        $( document ).ready(function() {
            var prices = [];
            prices.push(price_product);
            $("select").val('2').change();
            prices.push(price_product);
            $("select").val('3').change();
            prices.push(price_product);
            $("select").val('4').change();
            prices.push(price_product);
            $("select").val('5').change();
            prices.push(price_product);
            return prices
        });
    '''
    prices = await html.arender(script=script, timeout=100)
    soup = BeautifulSoup(html.html, 'lxml')
    image_src = soup.find('image').get('href')
    options = []
    for price, option_tag in zip(prices, soup.find(id='_sV').find_all('option')):
        option = Option(option_tag.text.strip(), price)
        options.append(option)

    product = Product(name, category, image_src, code, options)
    return product


k = 0
c = 0


async def get_products(category: Category) -> list[Product]:
    session = requests_html.AsyncHTMLSession()
    response = await session.get(category.url)
    html = response.html
    soup = BeautifulSoup(html.html, 'lxml')
    products = []
    for product_tag in soup.find_all('div', class_='product-thumb'):
        while True:
            try:
                product_url = product_tag.find('a').get('href')
                if product_url == 'https://modkartina.ru/all-news/novost1':
                    continue
                print(product_url)
                product = await get_product(product_url, category)
                products.append(product)
            except ElementHandleError:
                global k
                k += 1
                break
            except Exception as e:
                print(type(e))
                break
            else:
                print(product)
                break

    return products


async def main():
    tasks = []
    products = []
    for category in await get_categories():
        task = asyncio.create_task(get_products(category))
        tasks.append(task)

    for task in tasks:
        await task


if __name__ == "__main__":
    asyncio.run(main())
