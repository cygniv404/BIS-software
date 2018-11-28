import json
import os
import re
import sys

sys.path.append("/home/ahmedr/Documents/Backend-Retailstreets/venv")
import pandas as pd
import uuid


########################## FUNCTIONS ##########################

def get_shops(tenants):
    print(tenants)
    shops = []
    example = tenants.split("\n") or tenants.split("\r")

    for x in example:
        if len(x) > 0 and x != "CANT FIND":
            shop = "NaN"
            description = "NaN"
            if re.search("(.*)\\t.*", x):
                shop = re.search("(.*)\\t.*", x).group(1)
            if re.search("\\t([^\n]+)\\r", x):
                description = re.search("\\t([^\n]+)\\r", x).group(1)

            if re.search("(.*) {8,}.*", x):
                shop = re.search("(.*) {8,}.*", x).group(1)
            if re.search(" {7,}([^\n]+)", x):
                description = re.search(" {7,}([^\n]+)", x).group(1)

            shops += [{"name": shop, "description": description}]
    return shops


########################## DATA CONVERTING ####################################


shopping_street_path = "data/ShoppingStreet.json"
shoppings = []
data = pd.read_csv("data/Shopping-centers.csv")
data.replace("", "Not Available")

for index, s in data.iterrows():
    Mieter = "Not Available"
    if not (pd.isna(s[16])): Mieter = get_shops(s[16])
    shoppings += [{uuid.uuid4().__str__(): {"name": s[10].__str__(), "street": s[0].__str__(), "PLZ": s[1].__str__(),
                                            "city": s[2].__str__(), "region": s[3].__str__(),
                                            "open_year": s[4].__str__(), "location_type": s[5].__str__(),
                                            "n_shops": s[6].__str__(), "n_magnet_shops": s[7].__str__(),
                                            "area_total": s[8].__str__(), "area_rent": s[9].__str__(),
                                            "website": s[11].__str__(), "email": s[12].__str__(),
                                            "phone": s[13].__str__(), "parkinglots": s[14].__str__(),
                                            "open_time": s[15].__str__(), "shops": Mieter}}]


########################## WRITING TO ShoppingStreets.json ####################################

if os.stat(shopping_street_path).st_size == 0:
    with open(shopping_street_path, 'w') as outfile:
        json.dump(shoppings, outfile, ensure_ascii=False, indent=2)

    outfile.close()

