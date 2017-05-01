# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import logging
import requests
import json
import time
from pprint import pprint

# Instantiate logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MENUS_DIRECTORY = './menus/'

RAW_MENUS_DIRECTORY = MENUS_DIRECTORY + '/popchef/raw/'
CUSTOM_MENUS_DIRECTORY = MENUS_DIRECTORY + '/popchef/custom/'

# Add GET param : ?date=2017-05-01
POPCHEF_REQUEST_URL = "https://api.eatpopchef.com/api/schedules/next"

POPCHEF_BASE_URL = "https://eatpopchef.com"

POPCHEF_LOGO = "http://2015.fundtruck.com/wp-content/uploads/2015/08/274-2015-08-07-logo-profilpublicstartup.jpg"

##########################################################################
##############################      FILE MANAGEMENT      #################
##########################################################################


def create_directories_if_needed():
    if not os.path.exists(os.path.dirname(RAW_MENUS_DIRECTORY)):
        logger.info('Creating ' + RAW_MENUS_DIRECTORY + '...')
        try:
            os.makedirs(os.path.dirname(RAW_MENUS_DIRECTORY))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    if not os.path.exists(os.path.dirname(CUSTOM_MENUS_DIRECTORY)):
        logger.info('Creating ' + CUSTOM_MENUS_DIRECTORY + '...')
        try:
            os.makedirs(os.path.dirname(CUSTOM_MENUS_DIRECTORY))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def get_todays_raw_file_name():
    return 'popchef-raw-' + time.strftime("%d-%m-%Y") + '.json'


def get_todays_custom_file_name():
    return 'popchef-custom-' + time.strftime("%d-%m-%Y") + '.json'


def save_todays_menu_raw_format(menu):
    file_name = get_todays_raw_file_name()
    logger.info("Saving raw file " + file_name + " ...")
    with open(RAW_MENUS_DIRECTORY + file_name, 'w') as file:
        file.write(menu.text.encode('utf-8'))


def save_todays_menu_custom_format(menu):
    file_name = get_todays_custom_file_name()
    logger.info("Saving custom file " + file_name + " ...")
    # Do reformat here
    custom_menu = format_raw_menu(menu)
    with open(CUSTOM_MENUS_DIRECTORY + file_name, 'w') as file:
        file.write(json.dumps(custom_menu))


def format_raw_menu(raw_menu):
    custom_menu = {
        'menu': {},
        'meal_categories': []
    }
    if 'dishes' not in raw_menu:
    	return custom_menu

    for item in raw_menu['dishes']:
        meal_category = item['type']
        meal_category_label = {
            "dessert": "Desserts",
            "bread": "Pains",
            "beverage": "Boissons",
            "dish": "Plats",
            "starter": "Entrées",
            "other": "Autres"
        }[item['type']]

        new_meal_category = {
            'tag': meal_category,
            'label': meal_category_label
        }

        # Add category if not already present :
        if new_meal_category not in custom_menu['meal_categories']:
            custom_menu['meal_categories'].append(new_meal_category)
            custom_menu['menu'][meal_category] = []

        new_item = {
            'category_tag': meal_category,
            'category_label': meal_category_label,
            'title': item['title'],
            'price': item['price'],
            'productType': "Undefined",
            'productId': item['id'],
            'shortDescription': item['description'],
            'description': item['description'],
            'image': {
                'url': item['pictureThumb'],
                'id': ""
            }
        }

        custom_menu['menu'][meal_category].append(new_item)

    # Sort categories by alphabetical order
    custom_menu['meal_categories'] = sorted(
        custom_menu['meal_categories'], key=lambda n: n['label'])
    return custom_menu


##########################################################################
##############################        TODAYS MENU        #################
##########################################################################
def fetch_todays_popchef_menu():
    # Request Popchef's website to get daily data
    logger.info("Fetching today's data...")
    try:
        r = requests.get(POPCHEF_REQUEST_URL + "?date=" +
                         time.strftime("%Y-%m-%d"))
    except:
        r = None
    return r


def fetch_and_save_todays_menu_if_needed():
    create_directories_if_needed()
    if not os.path.exists(RAW_MENUS_DIRECTORY + get_todays_raw_file_name()) or not os.path.exists(CUSTOM_MENUS_DIRECTORY + get_todays_custom_file_name()):
        menu = fetch_todays_popchef_menu()
        save_todays_menu_raw_format(menu)
        with open(RAW_MENUS_DIRECTORY + get_todays_raw_file_name()) as data_file:
            json_menu = json.load(data_file)
            save_todays_menu_custom_format(json_menu)


def get_todays_data():
    with open(CUSTOM_MENUS_DIRECTORY + get_todays_custom_file_name()) as data_file:
        data = json.load(data_file)
    return data

##########################################################################
###################      USEFUL PRIVATE METHODS          #################


def get_product_url(product_id):
    return POPCHEF_BASE_URL


def get_propositions(selected_category):
    menu = get_todays_data()['menu']
    return [prop for prop in menu[selected_category]]


def get_todays_categories():
    data = get_todays_data()
    available_categories = [x for x in data['meal_categories']]
    return available_categories

##########################################################################
#########################      PUBLIC METHODS       ######################


def ask_popchef(query, param1=None):
    logger.info("Asking popchef for:\n  - query=%s\n  - param1=%s",
                query, param1)
    fetch_and_save_todays_menu_if_needed()
    if query == 'menu_categories':
        return get_todays_categories()
    elif query == 'propositions':
        return get_propositions(param1)
