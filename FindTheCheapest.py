import httpx
import asyncio
from selectolax.parser import HTMLParser
import time

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"}


async def get_html(client, url):
    resp = await client.get(url)
    return HTMLParser(resp.text)

def parse_page(html):
    products = html.css('li[class="max-md:border-b-size-sm max-md:border-color-default"]') # need to wrap it up because most parsers cant handle colons in the class names

    product_list = []

    for product in products:
        item = {
            "name": extract_text(product, ".mb-xs.font-bold"),
            "price": extract_text(product, "span[data-testid=product-price]"),
            "offers": extract_text(product, "span[data-testid=roundel]")
        }
        product_list.append(item)
    return product_list

def extract_text(html, sel):
    try:
        return html.css_first(sel).text()
    except AttributeError:
        return None

def clean_price(price_text):
    if not price_text:
        return None

    price_text = price_text.replace("£", "").replace(",", "").strip()

    # If it's a range like "20 - 30"
    if "-" in price_text:
        price_text = price_text.split("-")[0].strip()

    try:
        return float(price_text)
    except ValueError:
        return None

async def main():
    base_url = "https://www.diy.com/painting-decorating/paint.cat?Location=Interior&page="
    
    cheapest_item = None
    cheapest_price = float("inf")
    page = 1
    max_pages = 100

    async with httpx.AsyncClient(headers=headers, timeout=20) as client:
        tasks = []
        for page in range(1, max_pages + 1):
            url = base_url + str(page)
            tasks.append(get_html(client, url))

        pages = await asyncio.gather(*tasks)

        for html in pages:
            products = parse_page(html)

            for product in products:
                price = clean_price(product["price"])

                if price is not None and price < cheapest_price:
                    cheapest_price = price
                    cheapest_item = product

            page += 1

        print("\nCheapest product found:")
        print(cheapest_item)
        print("Price:", cheapest_price)

if __name__ == "__main__":
    asyncio.run(main())

# https://www.diy.com/painting-decorating/paint.cat?Location=Interior&page=2