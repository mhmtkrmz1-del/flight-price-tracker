import requests
import json

API_URL = "https://web.flypgs.com/pegasus/availability"

payload = {
    "flightSearchList": [
        {
            "departurePort": "CGN",
            "arrivalPort": "SAW",
            "departureDate": "2026-07-11"
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

headers = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://web.flypgs.com",
    "referer": "https://web.flypgs.com/booking",
    "user-agent": "Mozilla/5.0",
    "x-platform": "web",
    "x-version": "1.75.0",
}

response = requests.post(API_URL, json=payload, headers=headers, timeout=60)
data = response.json()

print(json.dumps(data)[:3000])

try:
    flights = data["departureRouteList"][0]["dailyFlightList"]

    prices = []
    for day in flights:
        date = day["date"]
        price = day["cheapestFare"]["amount"]
        prices.append({
            "date": date,
            "price": price
        })

    cheapest = min(prices, key=lambda x: x["price"])

    print("All prices:")
    for p in prices:
        print(p)

    print("\nCHEAPEST FLIGHT:")
    print(cheapest)

except Exception as e:
    print("Parsing error:", e)
