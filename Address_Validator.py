#!/usr/bin/python
"""
    VALIDATE THE MATCHED ADDRESSES WITH GOOGLE MAPS APIs
    IN ORDER TO OBTAIN WHICH ADDRESS IS CORRECT AND
    WHICH ONES NEEDS TO BE CHANGED
"""

import itertools
import json
import os
import re
import sys
import time
import uuid
from difflib import SequenceMatcher

import requests
import threading

business_address_path = "data/output_files/valid_address.json"
shoppingstreet_path = "data/output_files/shoppingstreet.json"
city_path = "data/output_files/city.json"
input_filename = "data/output_files/match.json"
input_filename1 = "data/output_files/cross_streets.json"
validated_streets_path = "data/intern_database/validated_streets.json"

done = False
valids = []

# ------------------ DATA LOADING --------------------------------

# load match.json file
with open(input_filename, 'r') as outfile:
    addresses = json.load(outfile)
outfile.close()

# load cross_street.json file
with open(input_filename1, 'r') as outfile:
    cross_streets = json.load(outfile)
outfile.close()

# loading valid_address file
if os.stat(validated_streets_path).st_size > 0:
    with open(validated_streets_path, 'r') as outfile:
        valids = json.load(outfile)
    outfile.close()


# ----------------- FUNCTION DEFINITIONS ------------------------
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


def similar(a, b):
    """
    :param a: string
    :param b: string
    :return: ratio of matching
    """
    return SequenceMatcher(None, a, b).ratio()


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


def get_city_name(city_id):
    """

    :param city_id: String city id to check
    :return: city name related, from city.json
    """
    city_name = None
    with open(city_path, "r+") as city_check:
        city_check.seek(0, os.SEEK_SET)
        cities = json.load(city_check)
    city_check.close()
    for citie in cities:
        if citie["city_id"] in city_id:
            city_name = citie["name"]

    return city_name


def index_of(val, in_list):
    """

    :param val: String variable to test
    :param in_list: list of Strings
    :return: index of the value if it's in the list
    """
    try:
        return in_list.index(val)
    except ValueError:
        return -1


def get_google_results(api_id, address, return_response_fields=None):
    """
    Get google results from Google Maps Geocoding API / Google Maps Places API / Google Maps Place details API

    :param: address: String address. Complete Address example "18 Starbucks Alexanderplatz, Berlin, Germany"
                    Address may vary based on the API used.

    :param: api_id: Number refers to which API is requested:
                    1: geocoding API
                    2: nearbysearch API

    :param: return_response_fields: Booleen/String indicate to return the full response from google if its None
                    Or returns specific fields. For example :"google_ratings,website,formated_address, etc."
    :return: Google result based on the api used

    """
    # set up api key
    api_key = "AIzaSyDQaVh67imEZW2FLH7hb33SB63jv2shkqQ"
    request_url = ""
    outputs = []
    building = address[0]
    address1 = address[0] + " " + address[1] + " " + address[2]
    if api_id == "geocoding":
        request_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}".format(
            address1) + "&key={}".format(
            api_key)
        print("GEOCODING |||||||||| " + request_url)
    if api_id == "nearbysearch":
        lat_long = get_google_results("geocoding", address, return_response_fields="latitude")[0][
                       "latitude"].__str__() + "," + \
                   get_google_results("geocoding", address, return_response_fields="longitude")[0][
                       "longitude"].__str__()
        request_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={}".format(
            lat_long) + "&rankby=distance&type=establishment&key={}".format(api_key)
        print("NEARBYSEARCH |||||||||| " + request_url)
    results = requests.get(request_url)
    results = results.json()

    if len(results['results']) == 0:
        return False
    else:
        for answer in results['results']:
            if api_id == "geocoding":

                street_number = "0"
                for y in answer.get('address_components'):
                    if 'street_number' in y.get('types'): street_number = y['long_name']

                route_name = "0"
                for z in answer.get('address_components'):
                    if 'route' in z.get('types'): route_name = z['long_name']

                output = {
                    "entry": building,
                    "street_number": street_number,
                    "route_name": route_name,
                    "latitude": answer.get('geometry').get('location').get('lat'),
                    "longitude": answer.get('geometry').get('location').get('lng'),
                    "google_place_id": answer.get("place_id"),
                    "type": ",".join(answer.get('types')),
                    "postcode": ",".join(
                        [x['long_name'] for x in answer.get('address_components') if 'postal_code' in x.get('types')]),

                }
                if (output["route_name"]) == "0":
                    output["route_name"] = answer.get('formatted_address')
                if (output["street_number"]) == "0":

                    pattern = re.compile("^(.+?),")
                    pattern0 = re.compile(",(.+?),")
                    patterns = [pattern, pattern0]
                    for pat in patterns:
                        if pat.search(answer.get('formatted_address')):

                            ad = re.findall(pat, answer.get('formatted_address'))[0]
                            pattern1 = re.compile("\d+")
                            if pattern1.search(ad):
                                ad1 = re.findall(pattern1, ad)[0]
                                if len(ad1) < 4: output["street_number"] = ad1

                outputs += [output]

            if api_id == "nearbysearch":
                street_number = "0"
                route_name = answer.get('vicinity')
                if answer.get('rating') is None:
                    rating = 0
                else:
                    rating = int(answer.get('rating'))

                output = {'input_string': address1, "street_number": street_number, "route_name": route_name,
                          "google_place_id": answer.get("place_id"), "type": ",".join(answer.get('types')),
                          "rating": rating}

                pattern = re.compile("^(.+?),")
                pattern0 = re.compile(",(.+?),")
                patterns = [pattern, pattern0]
                for pat in patterns:
                    if pat.search(route_name):

                        ad = re.findall(pat, answer.get('vicinity'))[0]
                        pattern1 = re.compile("\d+")
                        if pattern1.search(ad):
                            ad1 = re.findall(pattern1, ad)[0]
                            if len(ad1) < 4: output["street_number"] = ad1

                if output["street_number"] == address[0]:
                    outputs += [output]

    if return_response_fields is None and len(outputs) > 0:
        return outputs
    elif (len(outputs) > 0) and (return_response_fields is not None):
        output_filter = []
        for item in outputs:
            output_filter += [{"" + return_response_fields: item[return_response_fields]}]
        outputs = output_filter
        return outputs
    else:
        return False


def get_valid_business(street_number, street_name, city_name):
    """

    Search nearby the geocoded street address to find the related adresses
    :param street_number:String street number to search
    :param street_name: String street name
    :param city_name: String city name to search
    :return: most rated valid address or False

    """

    building = [street_number, street_name, city_name]
    result = get_google_results("nearbysearch", building, return_response_fields=None)
    if result:
        result = sorted(result, key=lambda k: k.get('rating', 0), reverse=True)[0]["google_place_id"]
        return result
    else:
        return False


def is_cross_street(street1, street2, city):
    """
     Test if 2 street crosses
    :param street1: String street name 2
    :param street2: String street name 1
    :param city: String city name
    :return: boolean
    """
    if get_google_results("geocoding", [street1, street2, city], return_response_fields=None):
        if "intersection" in get_google_results("geocoding", [street1, street2, city], return_response_fields=None)[0][
            "type"]:
            return True
    return False


def similarL1(a, b):
    """
    get similar between a string and a string in  a list
    :param a: String
    :param b: List of strings
    :return: boolean

    """
    if len(b) > 0:
        for x in b:
            if x == a:
                return True
    return False


def similarL1a(a, b):
    """
    get similar between a string in a list
    :param a: String
    :param b: List of strings
    :return: boolean

    """
    for x in b:
        if x.lower() in a.lower():
            return True
    return False


def similarL(a, b, ratio):
    """
    get similar ratio between a string in a list
    :param a: String
    :param b: List of strings
    :return:
    """
    for x in b:
        if SequenceMatcher(None, a, x).ratio() > ratio:
            return x
    return False


def in_suit(list, entry):
    """
    test 2 street numbers if the first in the second suit of numbers.
    For example: "25" in "22-27" retruns True
    :param a: String
    :param b: List of strings
    :return: boolean
    """
    text = list.replace("-", "")
    if ("-" not in entry) and (entry.isdigit() is True) and (text.isdigit() is True):
        list1 = list.split("-")
        x = int(list1[0])
        suit = set()
        suit.add(x)
        while x < int(list1[len(list1) - 1]):
            x += 1
            suit.add(x)
        suit.add(int(list1[len(list1) - 1]))
        if int(entry) in suit:
            return True
        else:
            return False
    return False


def in_suit1(list, entry):
    """
    test 2 street numbers if the second street number in the first suit of numbers.
    For example: "22-27" in "25"retruns True

    :param a: String List of number
    :param b: Int of number Number
    :return: boolean

    """
    text = list.replace("-", "")
    if ("-" not in entry) and (entry.isdigit() is True) and (text.isdigit() is True):
        list1 = list.split("-")
        x = int(list1[0])
        suit = set()
        suit.add(x)
        while x < int(list1[len(list1) - 1]):
            x += 1
            suit.add(x)
        suit.add(int(list1[len(list1) - 1]))
        if int(entry) in suit:
            return True
        else:
            return False
    return False


def in_suit3(list, list0):
    """

    test 2 suits of street numbers if they have crossed numbers
    For example: "22-27" in "21-24"retruns True

    :param a: Int of number
    :param b: String List of number
    :return: boolean


    """
    text = list.replace("-", "")
    text0 = list0.replace("-", "")
    if ("-" in list) and ("-" in list0) and (text.isdigit() is True) and (text0.isdigit() is True):

        list1 = list.split("-")
        x = int(list1[0])
        suit = set()
        suit.add(x)
        while x < int(list1[len(list1) - 1]):
            x += 1
            suit.add(x)
        suit.add(int(list1[len(list1) - 1]))

        list2 = list0.split("-")
        y = int(list2[0])
        suit0 = set()
        suit0.add(y)
        while y < int(list2[len(list2) - 1]):
            y += 1
            suit0.add(y)
        suit0.add(int(list2[len(list2) - 1]))
        temp = [item for item in suit if item in suit0]
        if len(temp) > 0: return True

    return False


# --------------------- MATCH.JSON VALIDATION------------------------------------------
print(
    "\n ################################# Matched addresses validation ######################################################")
t = threading.Thread(target=animate)
t.start()
# the valid business addresses found in the source file (valid name and street number)
businesses = []

# the invalid business addresses found in the source file (different number and valid street name)
not_valids = []

# street numbers without business name (extracted from the not_valid object)
incorrects = []

# the corrected street adresses without business name
businesses1 = []

cross_street_count = 0

for shop in addresses:

    is_validated = True
    for valid in valids:
        if shop["street_id"] == valid["street_id"] and valid["Address_Validator"] == False:
            is_validated = False

    if is_validated == False:
        street_name = get_street_name(shop["street_id"])
        city_name = get_city_name(shop["city_id"])

        business = {"street_id": shop["street_id"], "building": []}
        not_valid = {"building": []}
        incorrect = {"street_id": shop["street_id"], "city_id": shop["city_id"], "building": []}
        business_count = 0

        not_valid_count = 0
        incorrect_count = 0
        cross_street_list = set()

        for c in cross_streets:
            if c["street_id"] in shop["street_id"]:
                for b in c["cross_streets"]:
                    cross_street_list.add(b["name"])

        cross_street_list_count = len(cross_street_list)

        for entry in shop["building"]:
            if (entry["name"].lower() == "umbau") or (entry["name"].lower() == "neuvermietung"):
                incorrect["building"].extend({entry["number"]})
                incorrect_count += 1
            else:
                if get_google_results("geocoding", [entry["name"].lower(), street_name, city_name],
                                      return_response_fields=None):
                    result = get_google_results("geocoding", [entry["name"].lower(), street_name, city_name],
                                                return_response_fields=None)

                for r in result:

                    if (r["street_number"] is not "0") and (
                            (similarL1(r["street_number"], entry["number"].split("-"))) or
                            (r["street_number"] == entry["number"]) or
                            (similarL1(entry["number"], r["street_number"].split("-"))) or
                            ((in_suit(entry["number"], r["street_number"])) or
                             (in_suit1(r["street_number"], entry["number"])) or
                             (in_suit3(r["street_number"], entry["number"])))) and \
                            ((is_cross_street(r["route_name"].lower(), street_name.lower(), city_name.lower())) or \
                             ((street_name.lower() in r["route_name"].lower()) or
                              (similarL(r["route_name"].lower(), cross_street_list, 0.7)) or (
                              similarL1a(r["route_name"].lower(), cross_street_list)))):

                        if is_cross_street(r["route_name"].lower(), street_name.lower(), city_name.lower()) and \
                                ((is_cross_street(r["route_name"].lower(), street_name.lower(),
                                                  city_name.lower())) is False) and \
                                ((street_name.lower() not in r["route_name"].lower())):
                            cross_street_list.add(r["route_name"])
                            cross_street_count += 1
                            count_found = 0
                            for c in cross_streets:
                                if c["street_id"] in shop["street_id"]:
                                    for x in c["cross_streets"]:
                                        if r["route_name"].lower in x["name"].lower():
                                            count_found += 1
                                    if count_found < 1:
                                        c["cross_streets"].extend([{"cross_street_id": uuid.uuid4().__str__(),
                                                                    "name": r["route_name"].lower()}])

                        business["building"].extend({r["google_place_id"]})
                        business_count += 1

                    elif (r["street_number"] is not "0") and (
                            (is_cross_street(r["route_name"].lower(), street_name.lower(), city_name.lower())) or \
                            ((street_name.lower() in r["route_name"].lower()) or
                             (similarL(r["route_name"].lower(), cross_street_list, 0.7))) or (
                            similarL1a(r["route_name"].lower(), cross_street_list))):

                        if is_cross_street(r["route_name"].lower(), street_name.lower(), city_name.lower()) and \
                                ((is_cross_street(r["route_name"].lower(), street_name.lower(),
                                                  city_name.lower())) is False) and \
                                ((street_name.lower() not in r["route_name"].lower())):
                            cross_street_list.add(r["route_name"])
                            cross_street_count += 1
                            count_found = 0
                            for c in cross_streets:
                                if c["street_id"] in shop["street_id"]:
                                    for x in c["cross_streets"]:
                                        if r["route_name"].lower in x["name"].lower():
                                            count_found += 1
                                    if count_found < 1:
                                        c["cross_streets"].extend([{"cross_street_id": uuid.uuid4().__str__(),
                                                                    "name": r["route_name"].lower()}])

                        business["building"].extend({r["google_place_id"]})
                        business_count += 1

                        not_valid["building"].extend({entry["number"]})
                        not_valid_count += 1

                        incorrect["building"].extend({entry["number"]})
                        incorrect_count += 1

        if business_count > 0: businesses += [business]
        if not_valid_count > 0: not_valids += [not_valid]
        if incorrect_count > 0: incorrects += [incorrect]
        for valid in valids:
            if shop["street_id"] == valid["street_id"]:
                valid["Address_Validator"] = True

print("\n ---------------------Valid business from the source files--------------------------------------------------")
if len(businesses):
    print(json.dumps(businesses, ensure_ascii=False, indent=4))
else:
    print("\n No Valid Business Found")
print("\n --------------------------Incorrect Street Numbers--------------------------------------------------------")
if len(incorrects):
    print(json.dumps(incorrects, ensure_ascii=False, indent=4))
else:
    print("\n No Incorrect Addresses Found")

# ------------------CORRECT MISSING ADDRESS NAMES----------------------------------------------


for inc in incorrects:

    street_name = get_street_name(inc["street_id"])
    city_name = get_city_name(inc["city_id"])
    business1 = {"street_id": inc["street_id"], "building": []}
    business1_count = 0
    for entry in inc["building"]:
        valid_address = get_valid_business(entry, street_name, city_name)

        if valid_address:
            business1["building"].extend({valid_address})
            business1_count += 1
    if business1_count > 0: businesses1 += [business1]
if (len(businesses1) > 0):
    print(
        "\n --------------------------Corrected Businesses fetched--------------------------------------------------------")
    print(json.dumps(businesses1, ensure_ascii=False, indent=4))

# regrouping all businesses

for street in businesses:
    for street1 in businesses1:
        if street1["street_id"] == street["street_id"]:
            street["building"] = street["building"] + street1["building"]

################## WRITUNG IN JSON FILE ######################

# write to Valid_address.json

if os.stat(business_address_path).st_size == 0:
    with open(business_address_path, 'a') as outfile:

        json.dump(businesses, outfile, ensure_ascii=False, indent=2)
    outfile.close()
else:
    with open(business_address_path, 'a+') as outfile:

        outfile.seek(0, os.SEEK_SET)
        businesses1 = businesses
        potential_matchjson_d = json.load(outfile)
        for street in potential_matchjson_d:
            for street1 in businesses:
                if street1["street_id"] == street["street_id"]:
                    street["building"] = street["building"] + street1["building"]
                    businesses1.remove(street1)
        outfile.truncate(0)

        if len(businesses1) > 0: potential_matchjson_d.extend(businesses1)

        json.dump(potential_matchjson_d, outfile, ensure_ascii=False, indent=2)
    outfile.close()

# write in cross streets
if cross_street_count > 0:
    if os.stat(input_filename1).st_size == 0 and cross_streets.__len__() > 0:
        with open(input_filename1, 'a+') as outfile:

            json.dump(cross_streets, outfile, ensure_ascii=False, indent=4)

        outfile.close()
    else:
        with open(input_filename1, 'a+') as outfile:

            outfile.seek(0, os.SEEK_SET)
            cross_streets1 = cross_streets
            matchjson_d = json.load(outfile)
            for street in matchjson_d:
                for street1 in cross_streets:
                    if street1["street_id"] == street["street_id"]:
                        street["cross_streets"] = street1["cross_streets"]
                        cross_streets1.remove(street1)
            if len(cross_streets1) > 0: matchjson_d.extend(cross_streets1)
            json.dump(matchjson_d, outfile, ensure_ascii=False, indent=4)

outfile.close()
# write to validated_streets.json
# tracking which street was already validated to ensure a better use of the Google APIs.
if os.stat(validated_streets_path).st_size == 0:
    with open(validated_streets_path, 'a+') as outfile:

        json.dump(valids, outfile, ensure_ascii=False, indent=4)

    outfile.close()
else:
    with open(validated_streets_path, 'a+') as outfile:

        outfile.seek(0, os.SEEK_SET)

        outfile.truncate(0)

        json.dump(valids, outfile, ensure_ascii=False, indent=4)

    outfile.close()
done = True
