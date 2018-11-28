import os

# import files
dictionary2_ = "data/intern_database/dictionary2.txt"
dictionary3_ = "data/intern_database/dictionary3.txt"
validated_streets_ = "data/intern_database/validated_streets.json"
city_ = "data/output_files/city.json"
cross_streets_ = "data/output_files/cross_streets.json"
match_ = "data/output_files/match.json"
no_match_ = "data/output_files/no_match.json"
potential_match_ = "data/output_files/potential_match.json"
shoppingstreet_ = "data/output_files/shoppingstreet.json"
valid_address_ = "data/output_files/valid_address.json"

# delete file contents
with open(dictionary2_, "a+") as output_file:
    output_file.seek(0, os.SEEK_SET)
    output_file.truncate(0)
    dictionary2 = ["neuvermietung", "umbau", "eingang", "ausgang", "s u", "bahn", "station", "haltstelle", "amt",
                   "passage", "kirche"]
    dictionary2 = "\n".join(dictionary2)
    output_file.write(dictionary2)
output_file.close()
with open(dictionary3_, "a+")  as output_file:
    output_file.seek(0, os.SEEK_SET)
    output_file.truncate(0)
output_file.close()
with open(validated_streets_, "a+")  as output_file:
    output_file.seek(0, os.SEEK_SET)
    output_file.truncate(0)
output_file.close()
with open(city_, "a+") as output_file:
    output_file.seek(0, os.SEEK_SET)
    output_file.truncate(0)
output_file.close()
with open(cross_streets_, "a+") as output_file:
    output_file.seek(0, os.SEEK_SET)
    output_file.truncate(0)
output_file.close()
with open(match_, "a+")as output_file:
    output_file.seek(0, os.SEEK_SET)
    output_file.truncate(0)
output_file.close()
with open(no_match_, "a+") as output_file:
    output_file.seek(0, os.SEEK_SET)
    output_file.truncate(0)
output_file.close()
with open(potential_match_, "a+") as output_file:
    output_file.seek(0, os.SEEK_SET)
    output_file.truncate(0)
output_file.close()
with open(shoppingstreet_, "a+") as output_file:
    output_file.seek(0, os.SEEK_SET)
    output_file.truncate(0)
output_file.close()
with open(valid_address_, "a+") as output_file:
    output_file.seek(0, os.SEEK_SET)
    output_file.truncate(0)
output_file.close()
