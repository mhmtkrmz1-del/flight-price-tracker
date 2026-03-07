import json
from datetime import datetime

routes = [
    {"airline": "Pegasus", "from": "Köln", "to": "Sabiha Gökçen"},
    {"airline": "Pegasus", "from": "Düsseldorf", "to": "Sabiha Gökçen"},
    {"airline": "Pegasus", "from": "Rotterdam", "to": "Sabiha Gökçen"},
    {"airline": "Pegasus", "from": "Amsterdam", "to": "Sabiha Gökçen"},
    {"airline": "Pegasus", "from": "Dortmund", "to": "Sabiha Gökçen"},
    {"airline": "Pegasus", "from": "Brüksel", "to": "Sabiha Gökçen"},
    {"airline": "AJet", "from": "Köln", "to": "Sabiha Gökçen"},
    {"airline": "AJet", "from": "Düsseldorf", "to": "Sabiha Gökçen"},
    {"airline": "AJet", "from": "Rotterdam", "to": "Sabiha Gökçen"},
    {"airline": "AJet", "from": "Amsterdam", "to": "Sabiha Gökçen"},
    {"airline": "AJet", "from": "Dortmund", "to": "Sabiha Gökçen"},
    {"airline": "AJet", "from": "Brüksel", "to": "Sabiha Gökçen"},
]

prices = []

for r in routes:
    prices.append({
        "airline": r["airline"],
        "from": r["from"],
        "to": r["to"],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "price": 100
    })

with open("data/prices.json", "w") as f:
    json.dump(prices, f, indent=2)

print("prices.json updated")
