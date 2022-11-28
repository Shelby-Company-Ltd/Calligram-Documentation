#!/usr/bin/env python3
import sys
import json
import time
import os
import requests
import dateutil.parser as dp
from datetime import datetime


HN_REQUEST_TEMPLATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config",
    "hn",
    "hn.json",
)

with open(HN_REQUEST_TEMPLATE_FILE) as file:
    request_body = json.load(file)


##############################
# Calligram API specific logic
##############################


QUERY = sys.argv[1]
request_body["query"] = QUERY

CALLIGRAM_API_KEY = os.getenv("CALLIGRAM_API_KEY")
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


###############################
# HackerNews API specific logic
###############################


# Tags parameters


def get_tags_parameter(type: str, author: str) -> str:
    parameter_strings = []
    if type is not None:
        parameter_strings.append(type)
    if author is not None:
        parameter_strings.append(get_author_parameter(author))
    if len(parameter_strings) == 0:
        return None
    return ",".join(parameter_strings)


def get_author_parameter(author: str) -> str:
    return f"author_{author}"


# Numeric filters parameter


def get_numeric_filters(
    created_after: str | None,
    created_before: str | None,
    min_points: int | None,
    max_points: int | None,
    min_num_comments: int | None,
    max_num_comments: int | None,
) -> str | None:
    created_at_i = get_created_at_parameter(created_after, created_before)
    points = get_points_parameter(min_points, max_points)
    num_comments = get_num_comments_parameter(min_num_comments, max_num_comments)
    return get_numeric_filters_internal(created_at_i, points, num_comments)


def get_numeric_filters_internal(
    created_at_i: str, points: str, num_comments: str
) -> str | None:
    parameter_strings = []
    if created_at_i is not None:
        parameter_strings.append(created_at_i)
    if points is not None:
        parameter_strings.append(points)
    if num_comments is not None:
        parameter_strings.append(num_comments)
    if len(parameter_strings) == 0:
        return None
    return ",".join(parameter_strings)


def get_created_at_parameter(
    created_after: str | None, created_before: str | None
) -> str | None:
    created_after_ts = (
        None if created_after is None else get_timestamp_from_iso8601(created_after)
    )
    created_before_ts = (
        None if created_before is None else get_timestamp_from_iso8601(created_before)
    )
    parameter_strings = []
    if created_after_ts is not None:
        parameter_strings.append(f"created_at_i>{created_after_ts}")
    if created_before_ts is not None:
        parameter_strings.append(f"created_at_i<{created_before_ts}")
    if len(parameter_strings) == 0:
        return None
    return ",".join(parameter_strings)


def get_timestamp_from_iso8601(iso8601: str) -> int:
    utc_dt = dp.parse(iso8601)
    return int(utc_dt.timestamp())


def get_points_parameter(min_points: int | None, max_points: int | None) -> str | None:
    parameter_strings = []
    if min_points is not None:
        parameter_strings.append(f"points>{min_points}")
    if max_points is not None:
        parameter_strings.append(f"points<{max_points}")
    if len(parameter_strings) == 0:
        return None
    return ",".join(parameter_strings)


def get_num_comments_parameter(
    min_num_comments: int | None, max_num_comments: int | None
) -> str | None:
    parameter_strings = []
    if min_num_comments is not None:
        parameter_strings.append(f"num_comments>{min_num_comments}")
    if max_num_comments is not None:
        parameter_strings.append(f"num_comments<{max_num_comments}")
    if len(parameter_strings) == 0:
        return None
    return ",".join(parameter_strings)


HN_URL: str = "http://hn.algolia.com/api/v1/search"

CONVERSIONS_TO_METERS: dict = {
    "meters": 1,
    "feet": 0.3048,
    "kilometers": 1000,
    "miles": 1609.34,
}

PRICE_TO_INT: dict = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}

parameters = {
    "query": result["search query"],
    "tags": get_tags_parameter(result["item type"], result["author"]),
    "numericFilters": get_numeric_filters(
        result["created after"],
        result["created before"],
        result["minimum points"],
        result["maximum points"],
        result["minimum comments"],
        result["maximum comments"],
    ),
}

parameters = {k: v for (k, v) in parameters.items() if v is not None}

print(f"Hacker News API parameters = {parameters}")

hn_response = requests.get(HN_URL, params=parameters)

print(json.dumps(hn_response.json(), indent=2))

sys.exit(0)
