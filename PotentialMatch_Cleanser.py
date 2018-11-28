#!/usr/bin/python
"""
    POTENTIAL ADDRESS CLEANSING BASED ON GOOGLE GEOCODER API and SequenceMatcher
    RETURNS THE CROSS STREETS, POTENTIAL BUSINESSES AND THE NO MATCHES
"""
import json
import logging
import os
import re
import uuid
from difflib import SequenceMatcher

import itertools
import requests
import sys
import threading
import time

logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

shoppingstreet_path = "data/output_files/shoppingstreet.json"
city_path = "data/output_files/city.json"
input_filename = "data/output_files/potential_match.json"
input_filename1 = 'data/intern_database/dictionary1.txt'
input_filename2 = 'data/intern_database/dictionary2.txt'
input_filename3 = 'data/intern_database/dictionary3.txt'
input_filename4 = 'data/intern_database/streetvocabulary_types.txt'
input_filename5 = 'data/intern_database/business_types.txt'
cross_streetsfile_path = "data/output_files/cross_streets.json"
nomatchfile_path = "data/output_files/no_match.json"
valid_address_path = "data/output_files/valid_address.json"

cross_streets_count = 0
no_match_count = 0
cross_streets = []
potential_match = []
done = False

# ------------------ DATA LOADING ---------------------------------------------

# loading potential matches file
with open(input_filename, 'r') as outfile:
    addresses = json.load(outfile)
outfile.close()

# loading dictionary OSM germany streets ( Dictionary1 )
with open(input_filename1, 'r') as outfile:
    dictionary1 = outfile.read()
    dictionary1 = dictionary1.split("\n")
outfile.close()

# loading dictionary Street Vocabularies ( Dictionary2 )
with open(input_filename2, 'r') as outfile:
    dictionary2 = outfile.read()
    dictionary2 = dictionary2.split("\n")
outfile.close()

# loading dictionary no business ( Dictionary3 )
with open(input_filename3, 'r') as outfile:
    dictionary3 = outfile.read()
    if len(dictionary3) > 0:
        dictionary3 = dictionary3.split("\n")
    else:
        dictionary3 = []
outfile.close()

# loading StreetVocabulary Types
with open(input_filename4, 'r') as outfile:
    vocab_type = outfile.read()
    vocab_type = vocab_type.split("\n")
outfile.close()

# loading business Types
with open(input_filename5, 'r') as outfile:
    business_type = outfile.read()
    business_type = business_type.split("\n")
outfile.close()


# ----------------- FUNCTION DEFINITIONS --------------------------------

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
    sys.stdout.write('\r Done!     ')


def similar(a, b):
    """
    :param a: string
    :param b: string
    :return: ratio of matching
    """
    return SequenceMatcher(None, a, b).ratio()


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


def similarL1(a, b):
    """
    get similar between a string and a string in  a list
    :param a: String
    :param b: List of strings
    :return: boolean

    """
    for x in b:
        if x.lower() in a.lower():
            return True
    return False


def similarL2(a, b, ratio):
    """
    get similar ratio between a string in a list
    :param a: String
    :param b: List of strings
    :return:
    """
    for x in b:
        if SequenceMatcher(None, a.lower(), x.lower()).ratio() > ratio:
            return x
    return False


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


def get_citiy_name(city_id):
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


def get_cross_streets(address, related):
    """
    :param address:
    :return: True if entry is a cross street
    """
    pattern0 = re.compile("\-$")
    dic_pattern = {"strasse", "straße", "weg", "platz", "übergang", "durchgang", "allee"}
    address = address.replace('str.', 'straße')
    address = address.replace('pl.', 'platz')

    if -1 < address.find("-") < len(address) - 1:
        address = re.sub("-", " ", address)
    if len(address) < 7:
        return False

    for lines in dictionary1:
        if pattern0.search(address):
            for line in dic_pattern:
                if similar(re.sub(pattern0, line, address), lines) > 0.97:
                    return lines
        if similar(address, lines) > 0.97:
            return lines
        if 0.6 < similar(address, lines) < 0.7:
            for item in related:
                if (similar((address + " " + item), lines) > 0.9 or similar((item + " " + address), lines) > 0.9) and (
                        len(item) > 2):
                    return lines
    return False


def is_cross_street(street1, street2, city):
    """
    Test if 2 street crosses
   :param street1: String street name 2
   :param street2: String street name 1
   :param city: String city name
   :return: boolean
   """
    if "intersection" in get_google_results("geocoding", [street1, street2, city], return_response_fields=None)[0][
        "type"]:
        return True
    return False


def get_google_results(api_id, address, return_response_fields=None):
    """
    Get google results from Google Maps Geocoding API / Google Maps Places API / Google Maps Place details API

    @param address: String address. Complete Address example "18 Starbucks Alexanderplatz, Berlin, Germany"
                    Address may vary based on the API used.

    @param api_id: Number refers to which API is requested:
                    1: geocoding API
                    2: findplacefromtext API
                    3: nearbysearch API

    @param return_response_fields: Booleen/String indicate to return the full response from google if its None
                    Or returns specific fields. For example :"google_ratings,website,formated_address, etc."

    """

    # set up api key
    api_key = "AIzaSyDQaVh67imEZW2FLH7hb33SB63jv2shkqQ"

    request_url = ""
    outputs = []
    building = address[0]
    address = address[0] + " " + address[1] + " " + address[2]
    if api_id == "geocoding":
        request_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}".format(address) + "&key={}".format(
            api_key)

    if api_id == "nearbysearch":
        lat_long = get_google_results(1, address,
                                      return_response_fields="latitude").__str__() + "," + get_google_results(
            1, address, return_response_fields="longitude").__str__()
        request_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={}".format(
            lat_long) + "&rankby=distance&type=establishment&key={}".format(api_key)

    results = requests.get(request_url)

    results = results.json()

    if len(results['results']) == 0:
        outputs = ""
    else:
        for answer in results['results']:
            if api_id == "geocoding":
                output = {
                    "entry": building,
                    "street_number": [y['long_name'] for y in answer.get('address_components') if
                                      'street_number' in y.get('types')],
                    "route_name": [z['long_name'] for z in answer.get('address_components') if
                                   'route' in z.get('types')],
                    "latitude": answer.get('geometry').get('location').get('lat'),
                    "longitude": answer.get('geometry').get('location').get('lng'),
                    "google_place_id": answer.get("place_id"),
                    "type": ",".join(answer.get('types')),
                    "postcode": ",".join(
                        [x['long_name'] for x in answer.get('address_components') if 'postal_code' in x.get('types')]),

                }
                if len(output["street_number"]) < 1:
                    output["street_number"] = ["0"]
                if len(output["route_name"]) < 1:
                    output["route_name"] = [answer.get('formatted_address')]
                if "intersection" in output["type"]:
                    output["route_name"] = [building]

                outputs += [output]

    if return_response_fields is None:
        return outputs
    else:
        output_filter = []
        for item in outputs:
            output_filter += [{"" + return_response_fields: item[return_response_fields]}]
        outputs = output_filter
        return outputs


print(
    "\n ################################# Potential Matches Cleanser ######################################################")
t = threading.Thread(target=animate)
t.start()

result_google = []

vocabulary = []
business = []

vocabularies = []
businesses = []

for potential in addresses:

    street_id = potential["street_id"]
    city_id = potential["city_id"]
    street_name = get_street_name(street_id)
    city_name = get_citiy_name(city_id)

    # check if the street is already been cleaned
    # loading valid_address file
    valid_found = 0
    if os.stat(valid_address_path).st_size > 0:
        with open(valid_address_path, 'r') as outfile:
            valids = json.load(outfile)
        outfile.close()
        for v in valids:
            if v["street_id"] == street_id: valid_found += 1

    # ----- PROCESS 1 -------------CROSS STREETS FILTERING ---------------------------------

    if valid_found < 1:

        related_building = set()
        cross_street = [{"street_id": potential["street_id"], "cross_streets": []}]
        for item in potential["building"]: related_building.add(item)
        for j in potential["building"]:
            cr_str = get_cross_streets(j.lower(), related_building)
            if cr_str is not False:
                cross_street[len(cross_street) - 1]["cross_streets"] += [
                    {"cross_street_id": uuid.uuid4().__str__(), "name": cr_str.lower()}]
                cross_streets_count += 1
                potential["building"][index_of(j, potential["building"])] = ""

        if cross_streets_count > 0: cross_streets += cross_street

print(
    "\n ---------------------------- Cross Streets found with OSM's Streets database --------------------------------------")
print(json.dumps(cross_streets, ensure_ascii=False, indent=4))

# ------------------ BUSINESS & STREET VOCABULARIES FILTERING ---------------------------
# check if result have cross street:

for potential in addresses:
    street_id = potential["street_id"]
    city_id = potential["city_id"]
    street_name = get_street_name(street_id)
    city_name = get_citiy_name(city_id)
    vocabulary = [{"street_id": street_id, "vocabulary": [], "nobusiness": []}]
    vocabulary_count = 0
    business = [{"street_id": street_id, "building": []}]
    no_business_count = 0
    business_count = 0

    # check if the street is already been cleaned
    # loading valid_address file
    valid_found = 0
    if os.stat(valid_address_path).st_size > 0:
        with open(valid_address_path, 'r') as outfile:
            valids = json.load(outfile)
        outfile.close()
        for v in valids:
            if v["street_id"] == street_id: valid_found += 1

    if valid_found < 1:
        for entry in potential["building"]:
            if len(entry) > 0:

                is_not_similar = 0
                if similarL1(entry.lower(), dictionary2):
                    vocabulary[len(vocabulary) - 1]["vocabulary"] += {entry.lower()}
                    vocabulary_count += 1
                    is_not_similar += 1
                if similarL1(entry.lower(), dictionary3):
                    vocabulary[len(vocabulary) - 1]["nobusiness"] += {entry.lower()}
                    vocabulary_count += 1
                    is_not_similar += 1
                if is_not_similar < 1:
                    building = entry.lower()
                    result_google += get_google_results("geocoding", [building, street_name, city_name],
                                                        return_response_fields=None)

        cross_street_list = set()
        for c in cross_streets:
            if c["street_id"] is potential["street_id"]:
                for b in c["cross_streets"]:
                    cross_street_list.add(b["name"])

        cross_street_list_count = len(cross_street_list)

        if len(result_google) > 0:

            for result in result_google:

                if (is_cross_street(result["route_name"][0].lower(), street_name.lower(), city_name.lower())) and (
                        street_name.lower() not in result["route_name"][0].lower()) and \
                        (similarL2(result["route_name"][0], cross_street_list, 0.7) is False):
                    cross_street_list.add(result["route_name"][0])
                    count_found = 0
                    for c in cross_streets:
                        if c["street_id"] in potential["street_id"]:
                            for x in c["cross_streets"]:
                                if similar(result["route_name"][0].lower(), x["name"].lower()) > 0.7:
                                    count_found += 1
                            if count_found < 1:
                                c["cross_streets"].extend([{"cross_street_id": uuid.uuid4().__str__(),
                                                            "name": result["route_name"][0].lower()}])

                if similarL(result["route_name"][0].lower(), cross_street_list, 0.70) or street_name.lower() in \
                        result["route_name"][0].lower() or \
                        similarL1(result["route_name"][0].lower(), cross_street_list):
                    building_types = result["type"].split(",")

                    if len(set(building_types).intersection(vocab_type)) > len(
                            set(building_types).intersection(business_type)):
                        vocabulary[len(vocabulary) - 1]["vocabulary"] += {result["entry"].lower()}

                        vocabulary_count += 1
                        no_match_count += 1

                        dictionary2.append(result["entry"].lower())

                    if len(set(building_types).intersection(business_type)) > len(
                            set(building_types).intersection(vocab_type)):
                        business[len(business) - 1]["building"] += {result["google_place_id"]}

                        business_count += 1

                    if len(set(building_types).intersection(vocab_type)) < 1 and len(
                            set(building_types).intersection(business_type)) < 1 and (
                            "intersection" not in building_types):
                        vocabulary[len(vocabulary) - 1]["nobusiness"] += {result["entry"].lower()}
                        dictionary3.append(result["entry"].lower())
                        no_match_count += 1
        if (len(vocabulary[len(vocabulary) - 1]["vocabulary"]) > 0):
            vocabularies += vocabulary
        if (len(business[len(vocabulary) - 1]["building"]) > 0):
            businesses += business
        result_google = []
print(
    "\n ---------------------------------- Cross Streets after Google's verification ----------------------------------------------")
print(json.dumps(cross_streets, ensure_ascii=False, indent=4))

print("\n ---------------------------- Vocabularies & Nobusinesses --------------------------------------")
if (len(vocabularies) > 0):
    print(json.dumps(vocabularies, ensure_ascii=False, indent=4))
else:
    print("\n No Vocabularies found")
print("------------------------------All Businesses Retrieved ----------------------------------------")
if (len(businesses) > 0):
    print(json.dumps(businesses, ensure_ascii=False, indent=4))
else:
    print("\n No Businesses found")
print(dictionary2)
################## WRITING JSON FILES ###########################################

# cross_street.json data writing
if cross_streets_count > 0:
    if os.stat(cross_streetsfile_path).st_size == 0 and cross_streets.__len__() > 0:
        with open(cross_streetsfile_path, 'a+') as outfile:

            json.dump(cross_streets, outfile, ensure_ascii=False, indent=4)

        outfile.close()
    else:
        with open(cross_streetsfile_path, 'a+') as outfile:

            outfile.seek(0, os.SEEK_SET)
            cross_streets1 = cross_streets
            matchjson_d = json.load(outfile)
            for street in matchjson_d:
                for street1 in cross_streets:
                    if street1["street_id"] == street["street_id"]:
                        street["cross_streets"] = street1["cross_streets"]
                        cross_streets1.remove(street1)
            outfile.truncate(0)
            if len(cross_streets1) > 0: matchjson_d.extend(cross_streets1)
            json.dump(matchjson_d, outfile, ensure_ascii=False, indent=4)

outfile.close()

# dictionary2.txt data writing
if dictionary2.__len__() > 0:
    with open(input_filename2, 'a+') as outfile:
        outfile.seek(0, os.SEEK_SET)

        dictionary2 = "\n".join(dictionary2)
        outfile.truncate(0)
        outfile.write(dictionary2)

outfile.close()

# dictionary3.txt data writing
if dictionary3.__len__() > 0:
    with open(input_filename3, 'a+') as outfile:
        outfile.seek(0, os.SEEK_SET)
        dictionary3 = "\n".join(dictionary3)
        outfile.truncate(0)
        outfile.write(dictionary3)

    outfile.close()

# No_Match.json data writing
if len(vocabularies) > 0:
    if os.stat(nomatchfile_path).st_size == 0:
        with open(nomatchfile_path, 'a+') as outfile:

            json.dump(vocabularies, outfile, ensure_ascii=False, indent=4)

        outfile.close()
    else:
        with open(nomatchfile_path, 'a+') as outfile:

            outfile.seek(0, os.SEEK_SET)
            vocabularies1 = vocabularies
            matchjson_d = json.load(outfile)
            for street in matchjson_d:
                for street1 in vocabularies:
                    if street1["street_id"] == street["street_id"]:
                        street["vocabulary"] = street1["vocabulary"]
                        street["nobusiness"] = street1["nobusiness"]
                        vocabularies1.remove(street1)
            outfile.truncate(0)
            if len(vocabularies1) > 0: matchjson_d.extend(vocabularies1)
            json.dump(matchjson_d, outfile, ensure_ascii=False, indent=4)

outfile.close()

# Valid.json data writing
if len(businesses) > 0:
    if os.stat(valid_address_path).st_size == 0:
        with open(valid_address_path, 'a+') as outfile:

            json.dump(businesses, outfile, ensure_ascii=False, indent=4)

        outfile.close()
    else:
        with open(valid_address_path, 'a+') as outfile:

            outfile.seek(0, os.SEEK_SET)
            businesses1 = businesses
            matchjson_d = json.load(outfile)
            for street in matchjson_d:
                for street1 in businesses:
                    if street1["street_id"] == street["street_id"]:
                        street["building"] = street1["building"] + street["building"]
                        businesses1.remove(street1)
            outfile.truncate(0)
            if len(businesses1) > 0: matchjson_d.extend(businesses1)
            json.dump(matchjson_d, outfile, ensure_ascii=False, indent=4)

outfile.close()
done = True
