"""
Clean the Street database fetched from OpenStreetMap database.
Make it adequate to the matching process with the resulted Potential_Match.json file.

"""
import os
import re

# ------------------ Dictionary1 LOADING --------------------------------

input_street = 'data/intern_database/strassen_osm.txt'
strassens = []
lenzmin = 100
with open(input_street, 'r') as street_file:
    street_file.seek(0, os.SEEK_SET)
    strassen = street_file.readlines()
    for s in strassen:
        x = s.replace('str.', 'straße')
        x = re.sub('[!@#$.<>,\-]', ' ', x)
        x = re.sub('[\"]', '', x)
        x = re.sub(' +', ' ', x)
        x = x.lower()
        lenz = len(x)
        if lenz > 6:
            strassens.append(x)
street_file.close()
print(lenzmin)
with open("data/intern_database/dictionary1.txt", 'w') as dic_file:
    dic_file.seek(0, os.SEEK_SET)
    for s in strassens:
        dic_file.write(s)
dic_file.close()
