#!/usr/bin/env python3
import sys
import json
import time
import os
import requests


TEMPLATE_FILE = sys.argv[1]
QUERY = sys.argv[2]

with open(TEMPLATE_FILE) as file:
    request_body = json.load(file)

request_body["query"] = QUERY


###############
# Calligram API
###############


QUERY = sys.argv[1]
CALLIGRAM_API_KEY = os.getenv("CALLIGRAM_API_KEY")
YELP_API_KEY = os.getenv("YELP_API_KEY")
CALLIGRAM_API = "https://y7xqsccv49.execute-api.us-west-1.amazonaws.com/production/map"

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

result = response.json()["result"]


################################
# Yelp Fusion API specific logic
################################


YELP_URL: str = "https://api.yelp.com/v3/businesses/search"

PRICE_TO_INT: dict = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}

if "price" in result:
    result["price"] = PRICE_TO_INT[result["price"]]

if "categories" in result:
    result["categories"] = result["categories"].replace(" ", "").lower()

yelp_response = requests.get(
    YELP_URL, headers={"Authorization": f"Bearer {YELP_API_KEY}"}, params=result
)

print(json.dumps(yelp_response.json(), indent=2))

sys.exit(0)
