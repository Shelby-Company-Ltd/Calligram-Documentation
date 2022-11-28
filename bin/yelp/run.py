#!/usr/bin/env python3
import sys
import json
import time
import os
import requests


YELP_REQUEST_TEMPLATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config",
    "yelp",
    "yelp.json",
)

with open(YELP_REQUEST_TEMPLATE_FILE) as file:
    request_body = json.load(file)


##############################
# Calligram API specific logic
##############################


QUERY = sys.argv[1]
request_body["query"] = QUERY

CALLIGRAM_API_KEY = os.getenv("CALLIGRAM_API_KEY")
YELP_API_KEY = os.getenv("YELP_API_KEY")
CALLIGRAM_API = "https://j2dqrphsbg.execute-api.us-west-1.amazonaws.com/production/map"

st = time.time()
response = requests.post(
    CALLIGRAM_API, json=request_body, headers={"X-API-KEY": CALLIGRAM_API_KEY}
)
print(
    "response received from Calligram with status code = {} in {} seconds".format(
        response.status_code, time.time() - st
    )
)
data = response.json()
print("response = {}".format(data))

result = data["result"]


################################
# Yelp Fusion API specific logic
################################

YELP_CATEGORIES_FILE: str = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config",
    "yelp",
    "yelp_categories.json",
)
with open(YELP_CATEGORIES_FILE) as file:
    CATEGORIES = json.load(file)

YELP_ALIASES_TO_TITLES = {
    category["alias"]: category["title"] for category in CATEGORIES
}
YELP_TITLES_TO_ALIASES = {
    category["title"]: category["alias"] for category in CATEGORIES
}


# NOTE: `YELP_CATEGORY_TAXONOMY` is unused in this script, but we have chosen to leave
# the following code here to demonstrate how we can generate a Calligram API conforming
# taxonomy from a real API example obtained directly from
# https://www.yelp.com/developers/documentation/v3/all_category_list/categories.json.
YELP_CATEGORY_TAXONOMY: list = [
    {
        "name": category["title"],
        "parents": [YELP_ALIASES_TO_TITLES[parent] for parent in category["parents"]],
    }
    for category in CATEGORIES
]
YELP_CATEGORY_TAXONOMY = [{"name": "Business", "parents": []}] + [
    category | {"parents": ["Business"]} if len(category["parents"]) == 0 else category
    for category in YELP_CATEGORY_TAXONOMY
]


YELP_URL: str = "https://api.yelp.com/v3/businesses/search"

CONVERSIONS_TO_METERS: dict = {
    "meters": 1,
    "feet": 0.3048,
    "kilometers": 1000,
    "miles": 1609.34,
}

PRICE_TO_INT: dict = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}

parameters = {
    "term": result["search term"],
    "location": result["location"],
    "radius": None
    if (result["search radius"] is None) or (result["search radius units"] is None)
    else int(
        result["search radius"] * CONVERSIONS_TO_METERS[result["search radius units"]]
    ),
    "categories": YELP_TITLES_TO_ALIASES[result["category"]]
    if (result["category"] is not None) and (result["category"] != "Business")
    else None,
    "price": None
    if result["price range"] is None
    else str(PRICE_TO_INT[result["price range"]]),
    "open now": result["open now"],
}

parameters = {k: v for (k, v) in parameters.items() if v is not None}

print(f"Yelp Fusion API parameters = {parameters}")

yelp_response = requests.get(
    YELP_URL, headers={"Authorization": f"Bearer {YELP_API_KEY}"}, params=parameters
)

print(json.dumps(yelp_response.json(), indent=2))

sys.exit(0)
