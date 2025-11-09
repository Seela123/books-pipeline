import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time

BASE = "https://books.toscrape.com/"

def get_soup(url):
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    r.encoding = "utf-8"          # <-- force correct decoding
    return BeautifulSoup(r.text, "html.parser")

def parse_book_card(card, base_url=BASE):
    a = card.find("h3").find("a")
    rel = a.get("href")
    product_url = urljoin(base_url, rel)
    price = card.select_one(".price_color").text.strip()
    availability = card.select_one(".availability").text.strip()
    rating_class = card.select_one("p.star-rating")["class"]
    # rating_class e.g. ['star-rating', 'Three']
    rating = rating_class[1] if len(rating_class) > 1 else ""
    title = a["title"]
    return {"title": title, "price_raw": price,
            "availability_raw": availability, "rating_raw": rating,
            "product_url": product_url}

def scrape_all_pages():
    page = "catalogue/page-1.html"
    results = []
    # first page root is index.html
    url = BASE
    while True:
        soup = get_soup(url)
        for card in soup.select(".product_pod"):
            results.append(parse_book_card(card, base_url=url))
        next_btn = soup.select_one("li.next > a")
        if not next_btn:
            break
        next_rel = next_btn["href"]
        url = url.rsplit("/", 1)[0] + "/" + next_rel  # keep relative path
        time.sleep(0.2)
    return results

def clean_df(df):
    # price: '£51.77' -> 51.77
    df['price'] = df['price_raw'].str.replace('£','').astype(float)
    # rating: map words to numbers
    mapping = {'One':1,'Two':2,'Three':3,'Four':4,'Five':5}
    df['rating'] = df['rating_raw'].map(mapping).fillna(0).astype(int)
    # availability: try to extract number, otherwise 1/0
    df['in_stock'] = df['availability_raw'].str.contains('In stock')
    return df

if __name__ == "__main__":
    raw = scrape_all_pages()
    df = pd.DataFrame(raw)
    df = clean_df(df)

    # create folders if missing
    import os
    os.makedirs("data/bronze", exist_ok=True)

    # save to bronze layer
    output_path = "data/bronze/books_toscrape_raw_cleaned.csv"
    df.to_csv(output_path, index=False)

    print(f"✅ Saved cleaned data to {output_path} — rows: {len(df)}")
