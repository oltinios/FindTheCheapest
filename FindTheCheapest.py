import httpx
import asyncio
from selectolax.parser import HTMLParser
import time
import json

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
            "offers": extract_text(product, "span[data-testid=roundel]"),
            "image": extract_image(product)
        }
        product_list.append(item)
    return product_list

def extract_text(html, sel):
    try:
        return html.css_first(sel).text()
    except AttributeError:
        return None

def extract_image(html):
    try:
        img = html.css_first('[data-testid="product-image"]')
        if not img:
            return None
        # Use the highest resolution available
        return img.attrs.get("data-src") or img.attrs.get("src")
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

    all_products = []

    async with httpx.AsyncClient(headers=headers, timeout=20) as client:
        tasks = []
        for page in range(1, 100):  # reduce pages for testing, you can increase later
            url = base_url + str(page)
            tasks.append(get_html(client, url))

        pages = await asyncio.gather(*tasks)

        for html in pages:
            products = parse_page(html)
            all_products.extend(products)

    # Filter out products without a price
    valid_products = [
        p for p in all_products if clean_price(p["price"]) is not None
    ]

    # Sort by price
    valid_products.sort(key=lambda x: clean_price(x["price"]))

    # Return the top 6 cheapest items
    return valid_products[:1]

if __name__ == "__main__":
    import asyncio
    items = asyncio.run(main())
    for i, item in enumerate(items, start=1):
        print(f"{i}. {item['name']}")
        print("   Image URL:", item['image'])

# https://www.diy.com/painting-decorating/paint.cat?Location=Interior&page=2