import json
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

DATA_FILE = Path("data/prices.json")
DEBUG_FILE = Path("debug_output.txt")

CITY_TO_CODE = {
    "Köln": "CGN",
    "Sabiha Gökçen": "SAW"
}

def log_debug(message):
    with DEBUG_FILE.open("a", encoding="utf-8") as f:
        f.write(message + "\n")

def load_data():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def parse_price(text):
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else None

def scrape_pegasus(origin_code, dest_code, date):
    url = (
        "https://www.flypgs.com/en"
        f"?origin={origin_code}&destination={dest_code}"
        f"&departureDate={date}&adult=1&tripType=oneway"
    )

    log_debug(f"Pegasus URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)

            texts = page.locator("body").inner_text()

            prices = re.findall(r"\€\s?\d+", texts)

            if not prices:
                page.screenshot(path="pegasus_debug.png", full_page=True)
                log_debug("Pegasus price not found")
                return None

            values = [parse_price(p) for p in prices]
            values = [v for v in values if v]

            if not values:
                return None

            return min(values)

        finally:
            browser.close()

def scrape_ajet(origin, dest, date):

    url = "https://ajet.com/en-nl/flights"

    log_debug(f"AJet page opened")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)

            texts = page.locator("body").inner_text()

            prices = re.findall(r"\€\s?\d+", texts)

            if not prices:
                page.screenshot(path="ajet_debug.png", full_page=True)
                log_debug("AJet price not found")
                return None

            values = [parse_price(p) for p in prices]
            values = [v for v in values if v]

            if not values:
                return None

            return min(values)

        finally:
            browser.close()

def main():

    if DEBUG_FILE.exists():
        DEBUG_FILE.unlink()

    data = load_data()

    for route in data["routes"]:

        origin = route["from"]
        dest = route["to"]

        pegasus_prices = []
        ajet_prices = []

        for d in route["dates"]:

            dt = datetime.strptime(d, "%d %B %Y")
            iso = dt.strftime("%Y-%m-%d")

            log_debug(f"Checking {origin} -> {dest} | {iso}")

            pegasus = scrape_pegasus(
                CITY_TO_CODE[origin],
                CITY_TO_CODE[dest],
                iso
            )

            ajet = scrape_ajet(origin, dest, iso)

            pegasus_prices.append(pegasus if pegasus else 999)
            ajet_prices.append(ajet if ajet else 999)

            log_debug(f"Pegasus={pegasus} AJet={ajet}")

        route["airlines"]["Pegasus"] = pegasus_prices
        route["airlines"]["AJet"] = ajet_prices

    save_data(data)

    log_debug("prices.json updated")

if __name__ == "__main__":
    main()
