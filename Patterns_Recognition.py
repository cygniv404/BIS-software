#!/usr/bin/python
"""
    CLEANSING THE .TXT DATA with RegularExpression and SequenceMatcher BASED ON ANALYSIS OF THE GIVEN PDFs DATA
    IN ORDER TO OBTAIN THE JSON FILES OF THE MATCHED ADDRESSES AND POTENTIAL MATCHES
"""

import json
import os
import re
from difflib import SequenceMatcher
from sys import path

path.append("/home/ahmedr/Documents/Backend-Retailstreets/venv/lib64/python3.6/site-packages")

shoppingstreet_path = "data/output_files/shoppingstreet.json"
city_path = "data/output_files/city.json"
matchfile_path = "data/output_files/match.json"
potential_matchfile_path = "data/output_files/potential_match.json"


########################################### FUNCTIONS ###########################################
def similar(a, b):
    """
    :param a: string
    :param b: string
    :return: ratio of matching[0-1]
    """
    return SequenceMatcher(None, a, b).ratio()


def main(arg1):
    print(
        "\n ################################# PATTERN RECOGNITION ######################################################")
    input_file_path = "3e36d5d2-e9df-40fd-947b-f3705c8f6c51_ad750b4a-061a-4e03-b3b4-ed1b5e9e1cc3.txt"

    try:
        if len(arg1) > 0 and os.stat(
            "data/texted_file/" + str(arg1)).st_size > 0: input_file_path = "data/texted_file/" + str(arg1)
    except Exception:
        exit("file not found: " + str(arg1))

    # texted file
    fp = open(input_file_path, "r")

    # get street_id and city_id from file name
    file_name = os.path.basename(fp.name)
    file_name = os.path.splitext(file_name)[0]
    city_id = file_name.split("_", 1)[0]
    street_id = file_name.split("_", 1)[1]

    city_name = ""
    street_name = ""
    # get city name
    with open(city_path, "r+") as city_check:
        city_check.seek(0, os.SEEK_SET)
        cities = json.load(city_check)
    city_check.close()
    for citie in cities:
        if citie["city_id"] in city_id:
            city_name = citie["name"]

    # get street name
    with open(shoppingstreet_path, "r+") as shop_check:
        shop_check.seek(0, os.SEEK_SET)
        shops = json.load(shop_check)
    shop_check.close()
    for shop in shops:
        if shop["street_id"] in street_id:
            street_name = shop["name"]

    ############################## PATTERNS FOR COMPLETE BUSINESS CREATION #############################

    # this is for "41-41.."
    pattern = re.compile("^(\d{1,3}\-\d{1,3})")
    # this is for "41a-41a.."
    pattern1 = re.compile("^(\d{1,3}[a-z]\-\d{1,3}[a-z])", re.IGNORECASE)
    # this is for "41a-41.."
    pattern2 = re.compile("^(\d{1,3}[a-z]\-\d{1,3})", re.IGNORECASE)
    # this is for "41-41a.."
    pattern3 = re.compile("^(\d{1,3}\-\d{1,3}[a-z])", re.IGNORECASE)
    # this is for "..41-41"
    pattern4 = re.compile("(\d{1,3}\-\d{1,3})$")
    # this is for "..41a-41a"
    pattern5 = re.compile("(\d{1,3}[a-z]\-\d{1,3}[a-z])$", re.IGNORECASE)
    # this is for "..41a-41"
    pattern6 = re.compile("(\d{1,3}[a-z]\-\d{1,3})$", re.IGNORECASE)
    # this is for "..41-41a"
    pattern7 = re.compile("(\d{1,3}\-\d{1,3}[a-z])$", re.IGNORECASE)
    # this is for "41.."
    pattern8 = re.compile("^(\d{1,3})")
    # this is for "41a.."
    pattern9 = re.compile("^(\d{1,3}[a-z])", re.IGNORECASE)
    # this is for "..41"
    pattern10 = re.compile("(\d{1,3})$")
    # this is for "..41a"
    pattern11 = re.compile("(\d{1,3}[a-z])$", re.IGNORECASE)

    # all patterns in one array
    patterns = [pattern, pattern2, pattern1, pattern3, pattern4, pattern5, pattern6, pattern7, pattern8, pattern9,
                pattern10, pattern11]

    #################### FILTERING MATCH ADRESSES FROM POTENTIAL ADRESSES ######################################

    # match addresses object
    adresses = [{"city_id": city_id, "street_id": street_id, "building": []}]
    # read text file into object
    potential_match = fp.read().splitlines()
    fp.close()
    # remove CITY_NAME and STREET_NAME from texted-file
    for m in potential_match[:]:
        if similar(city_name.lower(), m.lower()) > 0.7:
            potential_match.remove(m)

    for m in potential_match[:]:
        if similar(street_name.lower(), m.lower()) > 0.7:
            potential_match.remove(m)
    # check if entriy match patterns and load in match addresses object
    for line in potential_match:
        for b in adresses:
            for ptrn in patterns:
                if ptrn.search(line) and line.__len__() > 2:
                    match = [{"number": re.findall(ptrn, line)[0],
                              "name": re.sub(ptrn, '', line).__str__().lstrip(' ').rstrip()}]
                    b["building"].extend(match)

                    break

    # remove duplicated matched entries
    for n in adresses[0]["building"]:
        for m in potential_match:
            if similar((n["name"] + " " + n["number"]), m) > 0.90 or similar((n["number"] + " " + n["name"]), m) > 0.90:
                potential_match.remove(m)

    potential_match_final = [{"city_id": city_id, "street_id": street_id, "building": []}]

    for m in potential_match:
        for n in potential_match_final:
            n["building"].append(m)
    potential_match = potential_match_final

    ##################### WRITING TO JSON FILES ###################################

    # writing to Math.json file
    if os.stat(matchfile_path).st_size == 0:
        with open(matchfile_path, 'a+') as outfile:

            json.dump(adresses, outfile, ensure_ascii=False, indent=4)

        outfile.close()
    else:
        with open(matchfile_path, 'a+') as outfile:

            outfile.seek(0, os.SEEK_SET)

            matchjson_d = json.load(outfile)
            outfile.truncate(0)
            matchjson_d.extend(adresses)
            json.dump(matchjson_d, outfile, ensure_ascii=False, indent=4)

        outfile.close()

    # writing to Potential_.json file
    if os.stat(potential_matchfile_path).st_size == 0:
        with open(potential_matchfile_path, 'a') as outfile:

            json.dump(potential_match, outfile, ensure_ascii=False, indent=2)

        outfile.close()
    else:
        with open(potential_matchfile_path, 'a+') as outfile:

            outfile.seek(0, os.SEEK_SET)

            potential_matchjson_d = json.load(outfile)
            outfile.truncate(0)
            potential_matchjson_d.extend(potential_match)
            json.dump(potential_matchjson_d, outfile, ensure_ascii=False, indent=2)

        outfile.close()

    print("\n------------------------------------- Matched entries --------------------------------------------------")
    print(json.dumps(adresses, ensure_ascii=False, indent=4))
    print("\n------------------------------------ Not Matched entries -----------------------------------------------")
    print(json.dumps(potential_match, ensure_ascii=False, indent=4))
