"""
SAVE PICTURES FETCHED WITH GOOGLE MAP STATIC API IN LOCAL STORAGE
    ==> REDUCE THE USE OF GOOGLE MAPS REQUESTS
    :param (STRING) LONGITUDE AND LATITUDE
    :return (JPG) FILE
"""

import json
import os

import requests

# import source url files
business_path = "data/output_files/business.json"
with open(business_path, 'r') as inputfile:
    business = json.load(inputfile)
inputfile.close()


# ----------------- FUNCTION DEFINITIONS ------------------------

def Fetch_image(_mapid, _dirname, _filename):
    """

    :param _mapid: (string) Langitude and Altitude of the targeted place

    """
    api_key = "AIzaSyDQaVh67imEZW2FLH7hb33SB63jv2shkqQ"
    request_url = "https://maps.googleapis.com/maps/api/staticmap?center={}".format(_mapid) + \
                  "&zoom=17&size=600x600&maptype=terrain&markers=size:large|color:purple|{}" \
                      .format(_mapid) + "&key={}".format(api_key)
    imagedata = requests.get(request_url).content
    Save_image(imagedata, _dirname, _filename)


def Save_image(_imagedata, _dirname, _filename):
    """

    :param _imagedata:(Array) Image data fetched
    :param _dirname: (String) destination directory file name
    :param _filename: (String) destination file name
    :return:

    """
    dirpath = "data/img/" + _dirname
    try:
        if os.path.exists(dirpath) is False:
            os.mkdir("data/img/" + _dirname)
        _dest = "data/img/" + _dirname + "/" + _filename + ".png"
        with open(_dest, 'wb') as handler:
            handler.write(_imagedata)
        handler.close()
    except Exception:
        print("the business \'" + _dirname + "\' is not saved")


# ---------------- FETCHING LANGITUDE AND LATITUDE--------------

print("Fetching " + str(len(business)) + " Businesses...")

for street in business:

    keys = list(street.keys())
    _key = keys[1]
    dir_name = street['street_id'].__str__()
    file_name = keys[1].__str__()
    dest = "data/img/" + dir_name + "/" + file_name + ".png"

    # test if the file already fetched
    if (os.path.exists(dest) is False):
        Fetch_image(street[_key]['map_id'], dir_name, file_name)

print("Done    %")
