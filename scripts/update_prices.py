import json
import re
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

DATA_FILE = Path("data/prices.json")

CITY_TO_CODE = {
    "Köln": "CGN",
    "Düsseldorf": "DUS",
    "Rotterdam": "RTM",
    "Amsterdam": "AMS",
    "Dortmund": "DTM",
    "Brüksel": "BRU",
    "Sabiha Gökçen": "SAW",
}

AJET_CITY_SLUG = {
    "Amsterdam": "amsterdam",
    "Brüksel": "brussels",
    "Düsseldorf": "dusseldorf",
    "Köln": "cologne",
    "Rotterdam": "rotterdam",
    "Dortmund": "dortmund",
    "Sabiha Gökçen": "istanbul",
}

def load_data():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def parse_price(text):
    if not text:
        return None
    cleaned = text.replace(",", ".")
    match = re.search(r"(\d+(?:\.\d{1,2})?)", cleaned)
    return float(match.group(1)) if match else None

def try_click(page, selectors):
    for selector in selectors:
        try:
            page.locator(selector).first.click(timeout=3000)
            return True
        except Exception:
            pass
    return False

def try_fill(page, selectors, value):
    for selector in selectors:
        try:
            loc = page.locator(selector).first
            loc.click(timeout=3000)
            loc.fill("")
            loc.fill(value)
            return True
        except Exception:
            pass
    return False

def extract_all_prices(page):
    texts = []
    selectors = [
        '[data-testid*="price"]',
        '[class*="price"]',
        '[class*="fare"]',
        'span:has-text("€")',
        'div:has-text("€")',
        'strong:has-text("€")',
    ]
    for selector in selectors:
        try:
            loc = page.locator(selector)
            count = min(loc.count(), 40)
            for i in range(count):
                txt = loc.nth(i).inner_text(timeout=1500).strip()
                if txt:
                    texts.append(txt)
        except Exception:
            pass

    values = [parse_price(t) for t in texts]
    values = [v for v in values if v is not None and v > 0]
    return values

def scrape_pegasus_one_way(origin_code, destination_code, depart_date):
    url = (
        "https://www.flypgs.com/en"
        f"?origin={origin_code}&destination={destination_code}"
        f"&departureDate={depart_date}&adult=1&tripType=oneway"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="en-GB")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            try_click(page, [
                'button:has-text("Accept")',
                'button:has-text("Allow all")',
                'button:has-text("I Accept")',
                'button:has-text("Kabul et")',
            ])

            try_click(page, [
                'button:has-text("Search")',
                'button:has-text("Show flights")',
                'button:has-text("Find flights")',
            ])

            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass

            prices = extract_all_prices(page)
            if not prices:
                page.screenshot(path="pegasus_debug.png", full_page=True)
                return None

            return min(prices)
        finally:
            browser.close()

def scrape_ajet_one_way(origin_city, destination_city, depart_date):
    """
    İlk canlı sürüm:
    AJet booking widget yerine deal sayfalarını deniyor.
    Bulamazsa None döner.
    """
    origin_slug = AJET_CITY_SLUG.get(origin_city)
    destination_slug = AJET_CITY_SLUG.get(destination_city)

    candidate_urls = []

    if origin_slug and destination_slug:
        candidate_urls.append(
            f"https://ajet.com/en-nl/flights-from-{origin_slug}"
        )
        candidate_urls.append(
            f"https://ajet.com/en-nl/flights-to-{destination_slug}"
        )

    candidate_urls.append("https://ajet.com/en-nl/flights")

    wanted_date = datetime.strptime(depart_date, "%Y-%m-%d").strftime("%d/%m/%Y")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="en-GB")

        try:
            for url in candidate_urls:
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                except Exception:
                    continue

                try_click(page, [
                    'button:has-text("Accept")',
                    'button:has-text("Allow all")',
                    'button:has-text("I Accept")',
                    'button:has-text("Kabul et")',
                ])

                body = page.locator("body").inner_text(timeout=5000)

                if origin_city in body or CITY_TO_CODE.get(origin_city, "") in body:
                    if destination_city in body or CITY_TO_CODE.get(destination_city, "") in body:
                        if wanted_date in body or depart_date in body:
                            prices = extract_all_prices(page)
                            if prices:
                                return min(prices)

                prices = extract_all_prices(page)
                if prices:
                    return min(prices)

            page.screenshot(path="ajet_debug.png", full_page=True)
            return None
        finally:
            browser.close()

def scrape_prices_for_route(route):
    origin = route["from"]
    destination = route["to"]
    direction = route["direction"]
    dates = route["dates"]

    pegasus_prices = []
    ajet_prices = []

    for human_date in dates:
        dt = datetime.strptime(human_date, "%d %B %Y")
        iso_date = dt.strftime("%Y-%m-%d")

        origin_code = CITY_TO_CODE[origin]
        destination_code = CITY_TO_CODE[destination]

        pegasus_price = scrape_pegasus_one_way(origin_code, destination_code, iso_date)
        ajet_price = scrape_ajet_one_way(origin, destination, iso_date)

        pegasus_prices.append(int(pegasus_price) if pegasus_price else 999)
        ajet_prices.append(int(ajet_price) if ajet_price else 999)

        print(
            f"{direction} | {origin} -> {destination} | {human_date} | "
            f"Pegasus={pegasus_prices[-1]} | AJet={ajet_prices[-1]}"
        )

    return pegasus_prices, ajet_prices

def main():
    data = load_data()

    for route in data["routes"]:
        pegasus_prices, ajet_prices = scrape_prices_for_route(route)
        route["airlines"]["Pegasus"] = pegasus_prices
        route["airlines"]["AJet"] = ajet_prices

    data["updatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    save_data(data)
    print("prices.json updated")

if __name__ == "__main__":
    main()
