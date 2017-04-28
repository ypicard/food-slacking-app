# -*- coding: utf-8 -*-

# This script should be called every day (maybe not the week-ends ?)
# to automatically make the bot post a message in each team it belongs to,
# to remind users to check for the day's menus

import os
from pprint import pprint
from pymongo import MongoClient
from slackclient import SlackClient
import logging

# Instantiate logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logging.info("Daily task called : send_daily_notifications")

MONGODB_URL = os.environ.get("MONGODB_URI")
logging.info("Connecting to database : " + MONGODB_URL)
mongo = MongoClient(MONGODB_URL)
# Some problem might occur here, set this as env variable maybe
db = mongo.local_food_slacking

all_credentials = db.credentials.find()

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

    response = [
        {
            'color': '#36a64f',
            'pretext': "Il serait peut être temps de savoir ce que l'on mange ce midi !",
            'callback_id': 'food_provider_selection',
            'actions': [
                {
                    'name': 'choice',
                    'text': 'Frichti',
                    'type': 'button',
                    'value': 'frichti'
                }
            ]
        }
    ]

    for channel in channels_the_bot_belongs_to:
        logging.info("Sengind notification to:\n  - team_id : " + team_id + "\n  - channel_id : " +
                     channel['id'] + "\n  - channel_name : " + channel['name'])
        slack.api_call("chat.postMessage", token=bot_token, channel=channel[
                       'id'], attachments=response,  as_user=True)
        nb_notifications = nb_notifications + 1

logging.info("DONE : sent a total of " + str(nb_notifications) + " notifications")
logging.info("End of task : send_daily_notifications")
