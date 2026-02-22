import httpx
from selectolax.parser import HTMLParser

def get_html(base_url, page):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"}
    resp = httpx.get(base_url + str(page), headers=headers)
    html = HTMLParser(resp.text)
    return html

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
    return float(price_text.replace("£", "").replace(",", "").strip())

def main():
    base_url = "https://www.diy.com/painting-decorating/paint.cat?Location=Interior&page="
    
    cheapest_item = None
    cheapest_price = float("inf")
    page = 1

    while True:
        html = get_html(base_url, page)
        products = parse_page(html)

        if not products:
            break

        for product in products:
            price = clean_price(product["price"])

            if price and price < cheapest_price:
                cheapest_price = price
                cheapest_item = product

        page += 1

    print("\nCheapest product found:")
    print(cheapest_item)
    print("Price:", cheapest_price)

if __name__ == "__main__":
    main()

# https://www.diy.com/painting-decorating/paint.cat?Location=Interior&page=2