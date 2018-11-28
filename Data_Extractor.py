#!/usr/bin/python
"""
    TEXT EXTRACTOR BASED ON PDFlib TET LIBRARY
    RETURNS .TXT DATA WITH ALL THE TEXT INSIDE THE PDF
"""
import json
import os
import re
import uuid
from sys import exc_info, version_info
from traceback import print_tb, print_exc

from PDFlib.TET import *

# input file used
shoppingstreet_path = "data/output_files/shoppingstreet.json"
city_path = "data/output_files/city.json"
validated_streets_path = "data/intern_database/validated_streets.json"


############################## TEXT EXTRACTION ############################
def main(argv1):
    input_file_path = str(argv1)
    # extract city name and shopping street name from file
    name_pattern = re.compile("\/(.*)\.", re.IGNORECASE)
    name = re.search(name_pattern, input_file_path).group(1)
    name_pattern = re.compile("\/(.*)", re.IGNORECASE)
    name = re.search(name_pattern, name).group(1)
    name = re.sub("1", "", name)
    name = re.sub("2", "", name)

    city_name = name.split("_", 1)[0].lower()
    street_name = name.split("_", 1)[1].lower()
    street_id = uuid.uuid4()
    city_id = uuid.uuid4()

    IsNewCity = True
    textedfile = ""
    # check if city in city.json already exist
    if os.stat(city_path).st_size != 0:
        with open(city_path, "r+") as city_check:
            city_check.seek(0, os.SEEK_SET)
            cities = json.load(city_check)
        city_check.close()

        for citie in cities:
            if citie["name"].lower() in city_name.lower():
                IsNewCity = False
                city_id = citie["city_id"]

    # texted-pdf output file
    output_file = "data/texted_file/" + city_id.__str__() + "_" + street_id.__str__() + ".txt"

    # global option list */
    globaloptlist = "searchpath={{../data} {../../../resource/cmap}}"

    # document-specific option list */
    docoptlist = ""

    # page-specific option list */
    pageoptlist = "granularity=page"

    # separator used between lines extracted
    separator = "\n"

    try:
        try:

            tet = TET()

            if (version_info[0] < 3):
                fp = open(output_file, 'w')
            else:
                fp = open(output_file, 'w', 2, 'utf-8')

            tet.set_option(globaloptlist)

            doc = tet.open_document(input_file_path, docoptlist)

            if (doc == -1):
                raise Exception("Error " + repr(tet.get_errnum()) + "in "
                                + tet.get_apiname() + "(): " + tet.get_errmsg())

            # get number of pages in the document */
            n_pages = tet.pcos_get_number(doc, "length:pages")

            # loop over pages in the document */
            for pageno in range(1, int(n_pages) + 1):
                imageno = -1

                page = tet.open_page(doc, pageno, pageoptlist)

                if (page == -1):
                    print("Error " + repr(tet.get_errnum()) + "in "
                          + tet.get_apiname() + "(): " + tet.get_errmsg())
                    continue  # try next page */

                # text-filtering from special caracters
                text = tet.get_text(doc)
                text = text.replace("(", "")
                text = text.replace(")", "")
                text = text.replace("*", "")
                text = text.replace("!", "")
                text = text.replace("'", "")
                text = text.replace("/", " ")
                text = text.replace(".", "")
                text = text.replace("&", " ")
                text = text.split("\n")
                text1 = []
                lines_seen = set()
                for line in text:
                    if line not in lines_seen:
                        text1.append(line)
                        lines_seen.add(line)
                text = "\n".join(text1)
                textedfile = text1
                # writing to texted-pdf file
                if text != None:
                    fp.write(text)

                if (tet.get_errnum() != 0):
                    print("\nError " + repr(tet.get_errnum())
                          + "in " + tet.get_apiname() + "() on page " +
                          repr(pageno) + ": " + tet.get_errmsg() + "\n")

                tet.close_page(page)

            tet.close_document(doc)
            fp.close()

        except TETException:
            print("TET exception occurred:\n[%d] %s: %s" %
                  ((tet.get_errnum()), tet.get_apiname(), tet.get_errmsg()))
            print_tb(exc_info()[2])


        except Exception:
            print("Exception occurred: %s" % (exc_info()[0]))
            print_exc()


    finally:
        tet.delete()

    # shoppingstreet and city JSON objects
    shoppingstreet = [{"street_id": street_id.__str__(), "name": street_name.__str__()}]
    city = [{"city_id": city_id.__str__(), "name": city_name.__str__()}]

    # validated_streets object (see the end)
    validated_street = [{"street_id": street_id.__str__(), "Address_Validator": False}]

    ################ WRITING TO JSON FILES ###########################

    # write to ShoppingStreet.json
    if os.stat(shoppingstreet_path).st_size == 0:
        with open(shoppingstreet_path, 'a+') as outfile:

            json.dump(shoppingstreet, outfile, ensure_ascii=False, indent=4)

        outfile.close()
    else:
        with open(shoppingstreet_path, 'a+') as outfile:

            outfile.seek(0, os.SEEK_SET)

            shop_streets = json.load(outfile)
            outfile.truncate(0)
            shop_streets.extend(shoppingstreet)

            json.dump(shop_streets, outfile, ensure_ascii=False, indent=4)

        outfile.close()

    # write to City.json
    if os.stat(city_path).st_size == 0:
        with open(city_path, 'a+') as outfile:

            json.dump(city, outfile, ensure_ascii=False, indent=4)

        outfile.close()
    else:
        with open(city_path, 'a+') as outfile:

            outfile.seek(0, os.SEEK_SET)

            citys = json.load(outfile)
            outfile.truncate(0)
            if IsNewCity == True: citys.extend(city)
            json.dump(citys, outfile, ensure_ascii=False, indent=4)

        outfile.close()
    # write to validated_streets.json
    # tracking which street was already validated to ensure a better use of the Google APIs.
    if os.stat(validated_streets_path).st_size == 0:
        with open(validated_streets_path, 'a+') as outfile:

            json.dump(validated_street, outfile, ensure_ascii=False, indent=4)

        outfile.close()
    else:
        with open(validated_streets_path, 'a+') as outfile:

            outfile.seek(0, os.SEEK_SET)

            val_streets = json.load(outfile)
            outfile.truncate(0)
            val_streets.extend(validated_street)

            json.dump(val_streets, outfile, ensure_ascii=False, indent=4)

        outfile.close()
    print("\n ################################# DATA EXTRACTOR ######################################################")
    print("\n ----------------------------------Shopping Street------------------------------------------------------")
    print(json.dumps(shoppingstreet, ensure_ascii=False, indent=4))
    print("\n  ------------------------------------- City ------------------------------------------------------------")
    print(json.dumps(city, ensure_ascii=False, indent=4))
    print("\n ---------------------------------Text Extracted -------------------------------------------------------")
    print(json.dumps(textedfile, ensure_ascii=False, indent=4))
    print(
        "\n ---------------------------------Validated_street -------------------------------------------------------")
    print(json.dumps(validated_street, ensure_ascii=False, indent=4))
    street_id = str(street_id)
    city_id = str(city_id)
    texted_file = city_id + "_" + street_id + ".txt"
    return texted_file
