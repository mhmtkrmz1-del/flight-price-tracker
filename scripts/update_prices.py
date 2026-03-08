import requests

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

print("STATUS:", response.status_code)
print("CONTENT-TYPE:", response.headers.get("content-type"))
print("TEXT START:")
print(response.text[:3000])
print("TEXT END")
