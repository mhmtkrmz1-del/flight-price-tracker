import json
from datetime import datetime
from pathlib import Path

import requests

DATA_FILE = Path("data/prices.json")
ARTIFACTS_DIR = Path("artifacts")
DEBUG_FILE = ARTIFACTS_DIR / "debug_output.txt"

CITY_TO_CODE = {
    "Köln": "CGN",
    "Düsseldorf": "DUS",
    "Rotterdam": "RTM",
    "Amsterdam": "AMS",
    "Dortmund": "DTM",
    "Brüksel": "BRU",
    "Sabiha Gökçen": "SAW",
}

API_URL = "https://web.flypgs.com/pegasus/availability"


def ensure_artifacts_dir():
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def log_debug(message):
    ensure_artifacts_dir()
    with DEBUG_FILE.open("a", encoding="utf-8") as f:
        f.write(str(message) + "\n")


def load_data():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_data(data):
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_payload(origin_code, destination_code, depart_date):
    return {
        "flightSearchList": [
            {
                "departurePort": origin_code,
                "arrivalPort": destination_code,
                "departureDate": depart_date,
            }
        ],
        "adultCount": 1,
        "childCount": 0,
        "infantCount": 0,
        "currency": "EUR",
        "dateOption": 1,
        "bookingType": "BOOKING",
        "operationCode": "TK",
        "ffRedemption": False,
        "expatPnr": False,
        "personnelFlightSearch": False,
        "totalPoints": None,
        "affiliate": {"id": None},
    }


def build_headers(origin_code, destination_code, depart_date):
    return {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://web.flypgs.com",
        "referer": (
            "https://web.flypgs.com/booking"
            f"?language=tr&adultCount=1&arrivalPort={destination_code}"
            f"&departurePort={origin_code}&currency=EUR&dateOption=1"
            f"&departureDate={depart_date}"
        ),
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36"
        ),
        "x-platform": "web",
        "x-version": "1.75.0",
    }


def scrape_pegasus_api(origin_code, destination_code, depart_date):
    payload = build_payload(origin_code, destination_code, depart_date)
    headers = build_headers(origin_code, destination_code, depart_date)

    log_debug(f"POST {API_URL}")
    log_debug(f"Payload: {json.dumps(payload, ensure_ascii=False)}")

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )

        log_debug(f"Status: {response.status_code}")
        response.raise_for_status()

        data = response.json()
        preview = json.dumps(data, ensure_ascii=False)[:3000]
        log_debug(f"Response preview: {preview}")

        route_list = data.get("departureRouteList", [])
        if not route_list:
            log_debug("No departureRouteList found")
            return None

        daily_flights = route_list[0].get("dailyFlightList", [])
        if not daily_flights:
            log_debug("No dailyFlightList found")
            return None

        match = None
        for item in daily_flights:
            if item.get("date") == depart_date:
                match = item
                break

        if match is None:
            match = daily_flights[0]

        cheapest_fare = match.get("cheapestFare")
        if cheapest_fare and cheapest_fare.get("amount") is not None:
            amount = cheapest_fare["amount"]
            log_debug(f"Pegasus cheapestFare amount: {amount}")
            return round(float(amount), 2)

        prices = []
        for flight in match.get("flightList", []):
            fare = flight.get("fare", {})
            shown = fare.get("shownFare", {})
            total = fare.get("totalFare", {})

            if shown.get("amount") is not None:
                prices.append(float(shown["amount"]))
            elif total.get("amount") is not None:
                prices.append(float(total["amount"]))

        if prices:
            amount = min(prices)
            log_debug(f"Pegasus fallback price: {amount}")
            return round(amount, 2)

        log_debug("No Pegasus fare found")
        return None

    except Exception as e:
        log_debug(f"Pegasus API exception: {e}")
        return None


def main():
    ensure_artifacts_dir()

    if DEBUG_FILE.exists():
        DEBUG_FILE.unlink()

    data = load_data()

    for route in data["routes"]:
        origin = route["from"]
        dest = route["to"]

        pegasus_prices = []
        ajet_prices = []

        origin_code = CITY_TO_CODE[origin]
        dest_code = CITY_TO_CODE[dest]

        for d in route["dates"]:
            dt = datetime.strptime(d, "%d %B %Y")
            iso = dt.strftime("%Y-%m-%d")

            log_debug(f"Checking {origin} -> {dest} | {iso}")

            pegasus = scrape_pegasus_api(origin_code, dest_code, iso)

            pegasus_prices.append(pegasus if pegasus is not None else 999)
            ajet_prices.append(999)

            log_debug(f"Result | Pegasus={pegasus} | AJet=SKIPPED")

        route["airlines"]["Pegasus"] = pegasus_prices
        route["airlines"]["AJet"] = ajet_prices

    data["updatedAt"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    save_data(data)
    log_debug("prices.json updated")


if __name__ == "__main__":
    main()
