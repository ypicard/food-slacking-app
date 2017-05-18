# -*- coding: utf-8 -*-

# This script should be called every day (maybe not the week-ends ?)
# to automatically make the bot post a message in each team it belongs to,
# to remind users to check for the day's menus

import os
from pprint import pprint
from pymongo import MongoClient
from slackclient import SlackClient
import logging
from random import shuffle
import json
import datetime

PROVIDER_CHOICES = [{
    'tag': 'frichti',
    'name': 'Frichti',
    'color':'#f7e77a',
    'has_api': True,
    'message': 'Voir le menu !',
    'thumb_url': "https://assets.chooseyourboss.com/companies/logos/000/006/214/square/22922_2_1459442348.png?1488874942"
},
    {
    'tag': 'popchef',
    'name': 'Popchef',
    'color':'#1ec28e',
    'has_api': True,
    'message': 'Voir le menu !',
    'thumb_url': "http://2015.fundtruck.com/wp-content/uploads/2015/08/274-2015-08-07-logo-profilpublicstartup.jpg"
},
    {
    'tag': 'ubereats',
    'name': 'UberEats',
    'color':'#1c95a5',
    'has_api': False,
    'website_url': "https://www.ubereats.com",
    'message': 'Allez sur le site !',
    'thumb_url': "http://cdn2.ubergizmo.com/wp-content/uploads/2016/01/ubereats-logo-640x640.jpg"
},
    {
    'tag': 'foodora',
    'name': 'Foodora',
    'color': '#d51965',
    'has_api': False,
    'website_url': "https://www.foodora.fr",
    'message': 'Allez sur le site !',
    'thumb_url': "http://www.chez-dang.com/wp-content/uploads/2017/02/foodora_web.png"
},
 {
    'tag': 'deliveroo',
    'name': 'Deliveroo',
    'color': '#21ccbe',
    'has_api': False,
    'website_url': "https://deliveroo.fr/fr/",
    'message': 'Allez sur le site !',
    'thumb_url': "http://www.underconsideration.com/brandnew/archives/deliveroo_logo.png"
},
    {
    'tag': 'pickles',
    'name': 'Pickles',
    'color': '#6da440',
    'has_api': True,
    'website_url': "https://www.pickles.fr/",
    'message': 'Montre moi le menu !',
    'thumb_url': "https://media-cdn.tripadvisor.com/media/photo-s/0e/30/2a/fe/logo.jpg"
},
    {
    'tag': 'nestor',
    'name': 'Nestor',
    'color': '#ef6537',
    'has_api': True,
    'website_url': "https://www.nestorparis.com/",
    'message': 'Montre moi le menu !',
    'thumb_url': "https://media.licdn.com/mpr/mpr/shrink_200_200/AAEAAQAAAAAAAAd9AAAAJDg4ZDQ2ZTg4LTM4OGMtNDZiYi1iNTRhLWNkNzcyNTc5YjkzNA.png"
}]

# Instantiate logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logging.info("Daily task called : send_daily_notifications")


# Only send a notification it it is a weekday
day_number_in_week = datetime.datetime.today().weekday()
logging.info("Day number in week : " + str(day_number_in_week))
logging.info("Should send a notification : " + str(day_number_in_week < 5))


if day_number_in_week < 5:

    MONGODB_URL = os.environ.get("MONGODB_URI")
    MONGODB_NAME = os.environ.get("MONGODB_NAME")

    logging.info("Connecting to database :\n  - MONGODB_URL=" +
                 MONGODB_URL + "\n  - MONGODB_NAME=" + MONGODB_NAME)
    mongo = MongoClient(MONGODB_URL)
    db = mongo[MONGODB_NAME]

    all_credentials = db.credentials.find()

    # Build notification to push to all team
    text = "Il serait peut etre temps de savoir ce que l'on mange ce midi !"

    # Build attachments
    attachments = []
    shuffle(PROVIDER_CHOICES)  # Randomize order
    for provider in PROVIDER_CHOICES:
        if provider['has_api']:
            new_attachment = {
                "title": provider['name'],
                "callback_id": "food_provider_selection",
                "color": provider['color'],
                "thumb_url": provider['thumb_url'],
                "attachment_type": "default",
                "actions": [{
                    "name": "choice",
                    "text": provider['message'],
                    "type": "button",
                    "value": provider['tag']
                }]
            }
        else:
            # If no API, just put a link to the website !
            new_attachment = {
                "title": provider['name'],
                "text": provider['website_url'],
                "callback_id": "food_provider_selection",
                "color": provider['color'],
                "thumb_url": provider['thumb_url'],
                "attachment_type": "default",
            }
        attachments.append(new_attachment)
    attachments = json.dumps(attachments)


    # For each team registered, check all channels to check if our bot belongs
    # to one of them, and post a message there !
    logging.info("Sending notification to each subscribed channel...")
    nb_notifications = 0
    for cred in all_credentials:
        team_id = cred['team_id']
        bot_id = cred['bot_id']
        bot_token = cred['bot_token']
        slack = SlackClient(bot_token)

        team_channels = slack.api_call(
            "channels.list", token=bot_token)['channels']
        channels_the_bot_belongs_to = [
            c for c in team_channels if c['is_member'] == True]

        for channel in channels_the_bot_belongs_to:
            logging.info("Sengind notification to:\n  - team_id : " + team_id + "\n  - channel_id : " +
                         channel['id'] + "\n  - channel_name : " + channel['name'])
            slack.api_call("chat.postMessage", token=bot_token, channel=channel[
                           'id'], text=text, attachments=attachments,  as_user=True)
            nb_notifications = nb_notifications + 1

    logging.info("DONE : sent a total of " +
                 str(nb_notifications) + " notifications")

logging.info("End of task : send_daily_notifications")
