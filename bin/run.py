#!/usr/bin/env python3
import sys
import json
import time
import os
import requests


YELP_REQUEST_TEMPLATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
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
print("response = {}".format(response.json()))

result = {k: v for (k, v) in response.json()["result"].items() if v is not None}


################################
# Yelp Fusion API specific logic
################################

YELP_CATEGORIES_FILE: str = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
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

PRICE_TO_INT: dict = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}

if "price" in result:
    result["price"] = PRICE_TO_INT[result["price"]]

if "category" in result:
    # NOTE: handle categorization of a business as the root "Business" category we
    # added above which is required for Calligram taxonomies to work properly
    if result["category"] == "Business":
        result.pop("category")
    else:
        result["category"] = YELP_TITLES_TO_ALIASES[result["category"]]

yelp_response = requests.get(
    YELP_URL, headers={"Authorization": f"Bearer {YELP_API_KEY}"}, params=result
)

print(json.dumps(yelp_response.json(), indent=2))

sys.exit(0)
