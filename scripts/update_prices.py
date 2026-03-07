from pathlib import Path
from datetime import datetime, timezone
import json

DATA_FILE = Path("data/prices.json")


def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {"updatedAt": "", "routes": []}


def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def update_route_price(data, direction, origin, destination, airline, prices):
    for route in data["routes"]:
        if (
            route["direction"] == direction
            and route["from"] == origin
            and route["to"] == destination
        ):
            route.setdefault("airlines", {})
            route["airlines"][airline] = prices
            return
    raise ValueError(f"Route not found: {direction} {origin} -> {destination}")


def scrape_pegasus_prices(origin, destination, dates, direction):
    sample = {
        ("Gidiş", "Köln"): [165, 171, 159, 177, 185, 157, 149, 161, 168],
        ("Gidiş", "Düsseldorf"): [168, 172, 164, 179, 188, 160, 154, 166, 171],
        ("Gidiş", "Rotterdam"): [158, 164, 152, 170, 178, 149, 142, 155, 161],
        ("Gidiş", "Amsterdam"): [172, 179, 168, 184, 194, 163, 158, 169, 176],
        ("Gidiş", "Dortmund"): [167, 173, 160, 176, 187, 156, 151, 163, 170],
        ("Gidiş", "Brüksel"): [175, 182, 171, 188, 196, 165, 160, 172, 179],
        ("Dönüş", "Sabiha Gökçen|Köln"): [169, 175, 163, 181, 188, 160, 152, 166, 173],
        ("Dönüş", "Sabiha Gökçen|Düsseldorf"): [172, 178, 168, 184, 191, 164, 156, 170, 176],
        ("Dönüş", "Sabiha Gökçen|Rotterdam"): [162, 169, 157, 176, 182, 154, 148, 160, 167],
        ("Dönüş", "Sabiha Gökçen|Amsterdam"): [176, 183, 170, 189, 197, 167, 161, 174, 180],
        ("Dönüş", "Sabiha Gökçen|Dortmund"): [167, 173, 161, 178, 185, 158, 150, 163, 169],
        ("Dönüş", "Sabiha Gökçen|Brüksel"): [174, 180, 169, 187, 195, 165, 159, 171, 178],
    }

    if direction == "Gidiş":
        return sample[(direction, origin)]
    return sample[(direction, f"{origin}|{destination}")]


def scrape_ajet_prices(origin, destination, dates, direction):
    sample = {
        ("Gidiş", "Köln"): [174, 180, 170, 186, 192, 167, 156, 172, 179],
        ("Gidiş", "Düsseldorf"): [175, 181, 173, 188, 194, 169, 159, 174, 180],
        ("Gidiş", "Rotterdam"): [166, 171, 160, 176, 184, 154, 150, 162, 169],
        ("Gidiş", "Amsterdam"): [178, 185, 173, 190, 198, 169, 164, 175, 181],
        ("Gidiş", "Dortmund"): [174, 179, 168, 183, 190, 162, 157, 169, 176],
        ("Gidiş", "Brüksel"): [181, 188, 176, 193, 201, 171, 166, 178, 184],
        ("Dönüş", "Sabiha Gökçen|Köln"): [176, 182, 171, 187, 194, 166, 159, 173, 179],
        ("Dönüş", "Sabiha Gökçen|Düsseldorf"): [178, 185, 174, 189, 197, 169, 162, 176, 182],
        ("Dönüş", "Sabiha Gökçen|Rotterdam"): [169, 174, 163, 179, 186, 158, 154, 166, 171],
        ("Dönüş", "Sabiha Gökçen|Amsterdam"): [182, 189, 177, 194, 202, 172, 168, 179, 186],
        ("Dönüş", "Sabiha Gökçen|Dortmund"): [174, 180, 168, 184, 191, 162, 157, 170, 176],
        ("Dönüş", "Sabiha Gökçen|Brüksel"): [181, 187, 175, 192, 199, 170, 165, 176, 183],
    }

    if direction == "Gidiş":
        return sample[(direction, origin)]
    return sample[(direction, f"{origin}|{destination}")]


def main():
    data = load_data()

    for route in data["routes"]:
        direction = route["direction"]
        origin = route["from"]
        destination = route["to"]
        dates = route["dates"]

        pegasus_prices = scrape_pegasus_prices(origin, destination, dates, direction)
        ajet_prices = scrape_ajet_prices(origin, destination, dates, direction)

        update_route_price(data, direction, origin, destination, "Pegasus", pegasus_prices)
        update_route_price(data, direction, origin, destination, "AJet", ajet_prices)

    data["updatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    save_data(data)
    print("prices.json updated")


if __name__ == "__main__":
    main()
