#!/usr/bin/python

import os
import logging
import requests
import json
import time
from pprint import pprint
from bs4 import BeautifulSoup
import urllib2
from pprint import pprint


# Instantiate logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MENUS_DIRECTORY = './menus/pickles'
RAW_MENUS_DIRECTORY = MENUS_DIRECTORY + '/raw/'
CUSTOM_MENUS_DIRECTORY = MENUS_DIRECTORY + '/custom/'

PICKLES_REQUEST_URL = "https://www.pickles.fr/"
PICKLES_BASE_URL = "https://www.pickles.fr/"
PICKLES_LOGO = "https://media-cdn.tripadvisor.com/media/photo-s/0e/30/2a/fe/logo.jpg"

##########################################################################
##############################      FILE MANAGEMENT      #################
##########################################################################


def create_directories_if_needed():
    if not os.path.exists(os.path.dirname(CUSTOM_MENUS_DIRECTORY)):
        logger.info('Creating ' + CUSTOM_MENUS_DIRECTORY + '...')
        try:
            os.makedirs(os.path.dirname(CUSTOM_MENUS_DIRECTORY))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def get_todays_custom_file_name():
    return 'pickles-custom-' + time.strftime("%d-%m-%Y") + '.json'


def save_todays_menu_custom_format(menu):
    file_name = get_todays_custom_file_name()
    logger.info("Saving custom file " + file_name + " ...")
    # Do reformat here
    custom_menu = fetch_todays_pickles_menu()
    with open(CUSTOM_MENUS_DIRECTORY + file_name, 'w') as file:
        file.write(json.dumps(custom_menu))


##########################################################################
##############################        TODAYS MENU        #################
##########################################################################
def fetch_todays_pickles_menu():

        # For pickles, I combined the fetching and the custom formatting

    # Request Pickles website to get daily data
    logger.info("Fetching today's data...")

    request = urllib2.urlopen(PICKLES_BASE_URL)
    logger.info("Parsing html with Beautifulsoup...")
    soup = BeautifulSoup(request, "html.parser")
    menu_dishes = soup.find_all('li', class_='menu-dishe')

    custom_menu = {'menu': {},
                   'meal_categories': []}
    only_pickles_category = {'tag': 'only_category',
                             'label': 'Enjoy !'}

    items = []
    for item in menu_dishes:
        new_item = {
            'category_tag': 'only_category',
            'category_label': 'Enjoy !',
            'title': item.h3.get_text(),
            'price':  item.find('sup', class_='currency').get_text()[:-1],
            'productType': None,
            'productId': '',
            'shortDescription': None,
            'description': None,
            'image': {
                'url': item.find('img')['src'],
                'id': None
            }
        }
        items.append(new_item)

    custom_menu['meal_categories'].append(only_pickles_category)
    custom_menu['menu']['only_category'] = items

    return custom_menu


def fetch_and_save_todays_menu_if_needed():
    create_directories_if_needed()
    if not os.path.exists(CUSTOM_MENUS_DIRECTORY + get_todays_custom_file_name()):
        menu = fetch_todays_pickles_menu()
        save_todays_menu_custom_format(menu)


def get_todays_data():
    with open(CUSTOM_MENUS_DIRECTORY + get_todays_custom_file_name()) as data_file:
        data = json.load(data_file)
    return data

##########################################################################
###################      USEFUL PRIVATE METHODS          #################


def get_product_url(product_id):
    return PICKLES_BASE_URL


def get_propositions(selected_category):
    menu = get_todays_data()['menu']
    pprint(menu)
    return [prop for prop in menu[selected_category]]

##########################################################################
#########################      PUBLIC METHODS       ######################


def ask_pickles(query, param1=None):
    logger.info("Asking pickles for:\n  - query=%s\n  - param1=%s",
                query, param1)
    fetch_and_save_todays_menu_if_needed()
    return get_propositions(param1)
