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

MENUS_DIRECTORY = './menus/frichti'

RAW_MENUS_DIRECTORY = MENUS_DIRECTORY + '/raw'
CUSTOM_MENUS_DIRECTORY = MENUS_DIRECTORY + '/custom'

FRICHTI_REQUEST_URL = "https://api-gateway.frichti.co/kitchens/7/menu"
# TODO : The kitchen id (number before menu iun url) seems to change the
# availabilities of some items : understand why
FRICHTI_BASE_URL = "https://www.frichti.co"

FRICHTI_LOGO = "https://assets.chooseyourboss.com/companies/logos/000/006/214/square/22922_2_1459442348.png?1488874942"

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
    return 'frichti-raw-' + time.strftime("%d-%m-%Y") + '.json'


def get_todays_custom_file_name():
    return 'frichti-custom-' + time.strftime("%d-%m-%Y") + '.json'


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
    custom_menu = {'menu': {},
                   'meal_categories': []}
    for item in raw_menu['menu']:
        meal_category = item['name']
        meal_category_label = item['label'].capitalize()

        new_meal_category_item = {'tag': meal_category,
                                  'label': meal_category_label}

        new_category_items = []
        for collect in item['collects']:
            if 'products' in collect.keys():
                old_item = collect['products']
                new_item = {
                    'category_tag': meal_category,
                    'category_label': meal_category_label,
                    'title': old_item['title'],
                    'price': old_item['variants'][0]['price'],
                    'productType': old_item['productType'],
                    'productId': old_item['productId'],
                    'shortDescription': old_item['shortDescription'],
                    'description': old_item['description'],
                    'image': {
                        'url': old_item['images'][0]['fullwidth'],
                        'id': old_item['images'][0]['id']
                    }
                }
                new_category_items.append(new_item)
        if new_category_items:
            custom_menu['meal_categories'].append(new_meal_category_item)
            custom_menu['menu'][meal_category] = new_category_items

    # Sort categories by alphabetical order
    custom_menu['meal_categories'] = sorted(
        custom_menu['meal_categories'], key=lambda n: n['label'])
    return custom_menu


##########################################################################
##############################        TODAYS MENU        #################
##########################################################################
def fetch_todays_frichti_menu():
    # Request Frichti website to get daily data
    logger.info("Fetching today's data...")
    try:
        r = requests.get(FRICHTI_REQUEST_URL)
    except:
        r = None
    return r


def fetch_and_save_todays_menu_if_needed():
    create_directories_if_needed()
    if not os.path.exists(RAW_MENUS_DIRECTORY + get_todays_raw_file_name()) or not os.path.exists(CUSTOM_MENUS_DIRECTORY + get_todays_custom_file_name()):
        menu = fetch_todays_frichti_menu()
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
    return FRICHTI_BASE_URL + '/p/' + product_id


def get_propositions(selected_category):
    menu = get_todays_data()['menu']
    return [prop for prop in menu[selected_category]]


def get_todays_categories():
    data = get_todays_data()
    available_categories = [x for x in data['meal_categories']]
    return available_categories

##########################################################################
#########################      PUBLIC METHODS       ######################


def ask_frichti(query, param1=None):
    logger.info("Asking frichti for:\n  - query=%s\n  - param1=%s", query, param1)
    fetch_and_save_todays_menu_if_needed()
    if query == 'menu_categories':
        return get_todays_categories()
    elif query == 'propositions':
        return get_propositions(param1)
