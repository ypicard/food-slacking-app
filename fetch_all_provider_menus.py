#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging

import frichti_api
import nestor_api
import popchef_api
import pickles_api

# Instantiate logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logging.info("Daily task called : fetch_all_provider_menus")
logging.info("Fetching Frichti menu...")
frichti_api.fetch_and_save_todays_menu_if_needed()

logging.info("Fetching Nestor menu...")
nestor_api.fetch_and_save_todays_menu_if_needed()

logging.info("Fetching Popchef menu...")
popchef_api.fetch_and_save_todays_menu_if_needed()

logging.info("Fetching Pickles menu...")
pickles_api.fetch_and_save_todays_menu_if_needed()

logging.info("Daily task called : fetch_all_provider_menus")