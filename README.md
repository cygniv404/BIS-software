# Business Information System 
> filtering business addresses from a two dimensional map and validate / correct / retrieve these business addresses via [Google Maps APIs](https://cloud.google.com/maps-platform/places/) and their related informations such as (location, phone, website, business type...)

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/facebook/react/blob/master/LICENSE) 
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
The Software's aim is to analyze and validate **PDF** data. These are shopping streets maps in 150 cities representing the compendium of the most important Shopping streets all around Germany.  

The aim of this project is to develop an data cleansing process, to cover all the necessary steps, to make the data usable for further processing. Based on the dataset extracted from the [ETL process](https://en.wikipedia.org/wiki/Extract,_transform,_load) used it should create a Business Information System. 
This system should have all the valid business informations retrieved and kept up to date.

A data acces portal [**RetailStreets**](https://retailstreet.herokuapp.com) is created to show the resulted business adresses and allow users to search through it. Here is a [**Live Version**](https://retailstreet.herokuapp.com/).  Give it a try!

For more detailed information on the Project: You can reffer to the [full documentation](https://www.web-profashion.de/Validation%20and%20Analysis%20for%20Business%20Information%20System.pdf).


## Source sample

Here are two examples of 2 shopping streets in germany:

![img](https://i.imgur.com/42HOj2E.png[/img])

------------

![img](https://i.imgur.com/uKitLUI.png[/img)


## Data Warehouse model
according to [McKelvey’s Model](https://www.researchgate.net/publication/316878885_The_Challenges_of_Data_Cleansing_with_Data_Warehouses) the business information system will be warehousing all the data retrieved from the ETL Process, which it will be the main core of the cleaning process of the source PDF files.

![img](https://i.imgur.com/hR3KnCn.png[/img)

## ETL Process

This is a flowchart presenting the diffrent stages and processes used to **extract**, **transform** and **load** the source file into clean, valid and correct ones.

![img](https://i.imgur.com/c7SlIOT.png[/img)

> For more detailed information on how different **Google maps APIs** are used and for what purpose, please refer to the  [full documentation](https://www.web-profashion.de/Validation%20and%20Analysis%20for%20Business%20Information%20System.pdf). 


------------

------------
 ## Requirements:
 
 **1. You need Python 3.4 or later to run mypy. You can have multiple Python versions (2.x and 3.x) installed on the same system without problems.**
  

In Ubuntu, Mint and Debian you can install Python 3 like this:

`sudo apt-get install python3 python3-pip`

For other Linux flavors, OS X and Windows, packages are available at
http://www.python.org/getit/

**2. The library **PDFlib TET** is used for text extraction from the source PDF files.**

**3. requests and panda.** 

 ## Setup:

comming soon...


------------


------------


## Author

Ahmed Riahi – [@LinkedIn](https://www.linkedin.com/in/ahmed-riahi-24011b85/)
