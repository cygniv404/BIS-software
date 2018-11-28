"""
                                              ___DATA CORRECTION WITH FACEBOOK___

REVERSE BUSINESS GEO-LOCATION USE GRAPH API TO GET THE COMPLETE BUSINESS ADDRESS OUT OF AN INCOMPLETE ADDRESS
:return INFORMATIONS OBJECTS ABOUT BUSINESS NAME AT AN EXACT LOCATION  OR null

"""

import facebook
import requests


def get_fb_info(places):
    if len(places) < 1:
        return False
    categories = []
    FACEBOOK_DIC = []

    for place in places["data"]:
        city = place['location'].get('city')
        street = place['location'].get('street')
        for x in place['category_list']:
            categories.extend({x["name"]})
        match = [{"region": {"name": city, "street": {"name": street,
                                                      "business": {"name": place["name"], "types": categories,
                                                                   "website": place["website"], "phone": place["phone"],
                                                                   "id": place["id"]}}}}]
        FACEBOOK_DIC.extend(match)
    return FACEBOOK_DIC


def get_fb_token(app_id, app_secret):
    url = 'https://graph.facebook.com/oauth/access_token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': app_id,
        'client_secret': app_secret
    }
    response = requests.post(url, params=payload)
    return response.json()['access_token']


# fb "id" and "secret id" from Facebook developer website
FACEBOOK_APP_ID = ''
FACEBOOK_APP_SECRET = ''
# streetname
street_name = "adalbertstrasse"
# authentification
graph = facebook.GraphAPI(access_token=get_fb_token(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET), version="2.10")
# request
places = graph.search(type='place',
                      q="esprit alexanderplatz berlin",
                      fields='name,location,category_list,picture,website,phone,hours')
# print result
print(places)
