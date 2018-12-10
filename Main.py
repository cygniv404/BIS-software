#!/usr/bin/python
"""
    Main Setup file to run the whole process for s given source data 
   
"""
import os
import time
from sys import argv, path

path.append("/home/ahmedr/Documents/Backend-Retailstreets/venv/lib/python3.6/site-packages")
import Data_Extractor
import Patterns_Recognition

input_file_path = ""
try:
    if len(argv[1]) > 0 and os.stat(
            "data/source_file/" + str(argv[1])).st_size > 0: input_file_path = "data/source_file/" + str(argv[1])
except Exception:
    exit("file not found: " + str(argv[1]))
os.system("python3 Reset_files.py")
texted_file = Data_Extractor.main(input_file_path)
Patterns_Recognition.main(texted_file)
time.sleep(10)
os.system("python3 PotentialMatch_Cleanser.py")
time.sleep(5)
os.system("python3 Address_Validator.py")
time.sleep(5)
os.system("python3 Information_Fetcher.py")
