#!/usr/bin/python
"""
    FETCH INFORMATION DETAILS ABOUT THE VALID ADDRESSES FROM GOOGLE PLACES DATABASE
    LOAD VOCABULARIES AND NO BUSINESSES IN THEIR RELATED JSON FILES
"""

import itertools
import json
import os
import sys
import threading
import uuid

import requests
import time

valid_address_path = "data/output_files/valid_address.json"
business_path = "data/output_files/business.json"
shoppingstreet_path = "data/output_files/shoppingstreet.json"
done = False
# ------------------------ DATA LOADING ------------------------------------------------------------------------
# get valid.json data and clean it from duplicated businesses
with open(valid_address_path, 'r') as outfile:
    addresses = json.load(outfile)
outfile.close()
for street in addresses:
    lines_seen = set()
    list1 = set()
    for line in street["building"]:
        if line not in lines_seen:
            list1.add(line)
            lines_seen.add(line)
    street["building"] = list1


# ---------------------- FUNCTION DEFINITIONS -----------------------------------------------------------------

def animate():
    """
    animation function for the terminal
    """
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rloading ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')


def get_street_name(street_id):
    """

    :param street_id: String shopping street id to check
    :return: street name related, from shoppingstreet.json
    """
    street_name = None
    with open(shoppingstreet_path, "r+") as shop_check:
        shop_check.seek(0, os.SEEK_SET)
        shops = json.load(shop_check)
    shop_check.close()
    for shop in shops:
        if shop["street_id"] in street_id:
            street_name = shop["name"]

    return street_name


def get_google_results(api_id, address, shoppingstreet, return_response_fields=None):
    """
    Get google results from Google Maps Geocoding API / Google Maps Places API / Google Maps Place details API

    @param address: String address. Complete Address example "18 Starbucks Alexanderplatz, Berlin, Germany"
                    Address may vary based on the API used.

    @param api_id: Number refers to which API is requested:

                    Google Place Details API


    @param return_response_fields: Booleen/String indicate to return the full response from google if its None
                    Or returns specific fields. For example :"google_ratings,website,formated_address, etc."

    """

    # set up api key
    api_key = "AIzaSyDQaVh67imEZW2FLH7hb33SB63jv2shkqQ"

    request_url = ""
    outputs = []
    building = address[0]

    if api_id == "details":
        request_url = "https://maps.googleapis.com/maps/api/place/details/json?placeid={}".format(
            address[0]) + "&rankby=distance&type=establishment&key={}".format(api_key)

    results = requests.get(request_url)

    # convert results to json format
    results = results.json()

    # if there's no results or an error, return empty results.
    if len(results['result']) == 0:
        outputs = [{{'input_string': building, "street_number": 0, "route_name": "0",
                     "google_place_id": "0", "type": "0",
                     "rating": 0}}]
    else:

        if api_id == "details":
            answer = results['result']

            region = "Germany"
            for w in answer.get('address_components'):
                if 'locality' in w.get('types'): region = w['long_name']
            open_time = "n.a"
            if (answer.get('opening_hours')) is not None:
                if (answer.get('opening_hours').get('weekday_text')) is not None:
                    open_time = answer.get('opening_hours').get('weekday_text')
            website = "n.a"
            if answer.get('website') is not None:
                website = answer.get('website')
            phone = "n.a"
            if answer.get('international_phone_number') is not None:
                phone = answer.get('international_phone_number')
            output = {
                "street_id": shoppingstreet,
                "region": region,
                "street_name": address[1],
                "address": answer.get("formatted_address"),
                "business_name": answer.get('name'),
                "business_website": website,
                "type": ",".join(answer.get('types')),
                "phone": phone,
                "icon": answer.get('icon'),
                "map": answer.get('geometry').get('location').get('lat').__str__() + "," + answer.get('geometry').get(
                    'location').get('lng').__str__(),
                "opentime": open_time,

            }
            outputs += [output]

    if return_response_fields is None and len(outputs) > 0:
        return outputs
    else:
        return False


print(
    "\n ############################## INFORMATION FETCHER ###########################################################")
t = threading.Thread(target=animate)
t.start()

result = []
businesses = []
for business in addresses:
    street_name = get_street_name(business["street_id"])
    for building in business["building"]:
        result += get_google_results("details", [building, street_name], str(business["street_id"]),
                                     return_response_fields=None)

for r in result:
    b = {
        "street_id": r["street_id"],
        str(uuid.uuid4()): {
            "street_name": r["street_name"],
            "city_name": r["region"],
            "business_name": r["business_name"],
            "full_address": r["address"],
            "website": r["business_website"],
            "type": r["type"],
            "icon_url": r["icon"],
            "map_id": r["map"],
            "phone": r["phone"],
            "opentime": r["opentime"]
        }
    }
    businesses += [b]
print("\n --------------------------businesses details fetched--------------------------------------------------------")
print(json.dumps(businesses, ensure_ascii=False, indent=4))

######################### WRITING IN JSON FILES ############################################################

# write in business.json
if os.stat(business_path).st_size == 0:
    with open(business_path, 'a') as outfile:

        json.dump(businesses, outfile, ensure_ascii=False, indent=2)
    outfile.close()
else:
    with open(business_path, 'a+') as outfile:

        outfile.seek(0, os.SEEK_SET)
        # businesses1=businesses
        matchjson_d = json.load(outfile)
        outfile.truncate(0)
        # for street in matchjson_d:
        #   for street1 in businesses:
        #       if street1[list(street1.keys())[1]]["map_id"] == street[list(street.keys())[1]]["map_id"]:
        #          businesses1.remove(street1)
        matchjson_d.extend(businesses)
        json.dump(matchjson_d, outfile, ensure_ascii=False, indent=2)
    outfile.close()
done = True
