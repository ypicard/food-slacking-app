# -*- coding: utf-8 -*-
#!/usr/bin/python


from datetime import datetime
import os
import logging
import requests
import json
import time
from pprint import pprint

# Instantiate logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MENUS_DIRECTORY = './menus/nestor'

RAW_MENUS_DIRECTORY = MENUS_DIRECTORY + '/raw/'
CUSTOM_MENUS_DIRECTORY = MENUS_DIRECTORY + '/custom/'

NESTOR_REQUEST_URL = "https://api-nestor.com/menu/75001"
# TODO : The kitchen id (number before menu iun url) seems to change the
# availabilities of some items : understand why
NESTOR_BASE_URL = "https://www.nestorparis.com/"

NESTOR_LOGO = "https://media.licdn.com/mpr/mpr/shrink_200_200/AAEAAQAAAAAAAAd9AAAAJDg4ZDQ2ZTg4LTM4OGMtNDZiYi1iNTRhLWNkNzcyNTc5YjkzNA.png"

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
    return 'nestor-raw-' + time.strftime("%d-%m-%Y") + '.json'


def get_todays_custom_file_name():
    return 'nestor-custom-' + time.strftime("%d-%m-%Y") + '.json'


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


def is_today(sample_date):
    sample_date = datetime.strptime(sample_date[0:10], "%Y-%m-%d").date()
    return datetime.today().day == sample_date.day and datetime.today().year == sample_date.year and datetime.today().month == sample_date.month


def format_raw_menu(raw_menu):
    custom_menu = {'menu': {},
                   'meal_categories': []}

    todays_menu = next(x['menus'][0] for x in raw_menu['menus']
                       if is_today(x['date']))
    meal_category = 'only_category'
    meal_category_label = "Menu du jour !"
    entree = {
        'category_tag': meal_category,
        'category_label': meal_category_label,
        'title': todays_menu['entree']['name'],
        'price': todays_menu['price']/100,
        'productType': 'entree',
        'productId': todays_menu['entree']['_id'],
        'shortDescription': "Entrée",
        'description': todays_menu['entree']['ingredients'],
        'image': {
            'url': todays_menu['entree']['image_url'],
            'id': ''
        }
    }
    dish = {
        'category_tag': meal_category,
        'category_label': meal_category_label,
        'title': todays_menu['dish']['name'],
        'price': todays_menu['price']/100,
        'productType': 'dish',
        'productId': todays_menu['dish']['_id'],
        'shortDescription': "Plat principal",
        'description': todays_menu['dish']['ingredients'],
        'image': {
            'url': todays_menu['dish']['image_url'],
            'id': ''
        }
    }
    dessert = {
        'category_tag': meal_category,
        'category_label': meal_category_label,
        'title': todays_menu['dessert']['name'],
        'price': todays_menu['price']/100,
        'productType': 'dessert',
        'productId': todays_menu['dessert']['_id'],
        'shortDescription': "Dessert",
        'description': todays_menu['dessert']['ingredients'],
        'image': {
            'url': todays_menu['dessert']['image_url'],
            'id': ''
        }
    }

    meal_category_item = {'tag': meal_category,
                          'label': meal_category_label}
    custom_menu['meal_categories'].append(meal_category_item)
    custom_menu['menu'][meal_category] = [entree, dish, dessert]

    return custom_menu


##########################################################################
##############################        TODAYS MENU        #################
##########################################################################
def fetch_todays_nestor_menu():
    # Request Nestor website to get daily data
    logger.info("Fetching today's data...")
    try:
        r = requests.get(NESTOR_REQUEST_URL)
    except:
        r = None
    return r


def fetch_and_save_todays_menu_if_needed():
    create_directories_if_needed()
    if not os.path.exists(RAW_MENUS_DIRECTORY + get_todays_raw_file_name()) or not os.path.exists(CUSTOM_MENUS_DIRECTORY + get_todays_custom_file_name()):
        menu = fetch_todays_nestor_menu()
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
    return NESTOR_BASE_URL


def get_propositions(selected_category):
    menu = get_todays_data()['menu']
    return [prop for prop in menu[selected_category]]


def get_todays_categories():
    data = get_todays_data()
    available_categories = [x for x in data['meal_categories']]
    return available_categories

##########################################################################
#########################      PUBLIC METHODS       ######################


def ask_nestor(query, param1=None):
    logger.info("Asking nestor for:\n  - query=%s\n  - param1=%s", query, param1)
    fetch_and_save_todays_menu_if_needed()
    return get_propositions(param1)
