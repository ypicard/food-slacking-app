# -*- coding: utf-8 -*-

import os
from slackclient import SlackClient
from flask import jsonify
from app_factory import mongo
from pprint import pprint
from frichti_api import *
import frichti_api
import copy

FOOD_CHOICES = ['frichti']

# TODO : Ajouter un boutton pour revenir en arriere a chaque etape


class FoodSlackingBot(object):

    """ Instanciates a Bot object to handle Slack interactions."""

    def __init__(self):
        super(FoodSlackingBot, self).__init__()
        self.name = "food_slacking_bot"
        self.emoji = ":robot_face:"
        self.id = ''
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        self.client = SlackClient("")

    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.

        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token

        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.api_call(
            "oauth.access",
            client_id=self.oauth["client_id"],
            client_secret=self.oauth["client_secret"],
            code=code
        )

        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        mongo.db.credentials.update({
            'team_id': auth_response["team_id"]
        }, {
            '$set': {'team_id': auth_response["team_id"],
                     'access_token': auth_response["access_token"],
                     'bot_id':  auth_response["bot"]["bot_user_id"],
                     'bot_token': auth_response["bot"]["bot_access_token"]
                     }
        }, True)

        # Reconnect the Slack Client with the correct bot token
        self.client = SlackClient(auth_response["bot"]["bot_access_token"])

    def authToCorrectTeam(self, team_id):
        team_credentials = mongo.db.credentials.find_one({'team_id': team_id})
        self.client = SlackClient(team_credentials['bot_token'])
        self.id = team_credentials['bot_id']

    def getAtBot(self):
        return '<@' + self.id + '>'

    def handle_command(self, team, channel, message):
        instructions = message.split()
        response = [
            {
                'color': '#36a64f',
                'pretext': 'Dites moi ce qui vous intéresse le plus aujourd\'hui !',
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

        self.client.api_call("chat.postMessage", token=team, channel=channel,
                             attachments=response, as_user=True)

    def format_menu_categories(self, provider, categories):
        # Returns a replacement response to replace the active Slack message,
        # and 'other_responses' which will appear as new messages

        response = {
            'text': 'Choisissez une catégorie pour connaitre ses choix :',
            'attachments': [{
                "author_name": provider.title(),
                "author_link": frichti_api.FRICHTI_BASE_URL,
                "author_icon": frichti_api.FRICHTI_LOGO
            }]
        }

        attachment_template = {
            'color': '36a64f',
            'pretext': "",
            'callback_id': 'menu_category_selection',
            'actions': []
        }

        new_attachment = copy.deepcopy(attachment_template)

        for idx, category in enumerate(categories):
            new_action = {
                'name': 'choice',
                'text': category['label'],
                'type': 'button',
                'value': provider + '/' + category['tag']
            }
            new_attachment['actions'].append(new_action)

            if idx > 0 and idx % 5 == 0:
                response['attachments'].append(new_attachment)
                new_attachment = copy.deepcopy(attachment_template)
        return response

    def format_propositions(self, provider, propositions):
        # Returns a replacement response to replace the active Slack message,
        # and 'other_responses' which will appear as new messages

        # response = {
        #     "text": "Liste des boissons Frichti : :",
        #     "attachments": [
        #         {
        #             "title": "Evian",
        #             "title_link": "http://df",
        #             "fields": [
        #                 {
        #                     "value": "Eau minérale naturelle finement pétillante.",
        #                     "short": true
        #                 }
        #             ],
        #             "thumb_url": "https://cdn.shopify.com/s/files/1/0832/9391/products/evian.jpg?v=1487582835",
        #             "color": "#7CD197"
        #         }
        #     ]
        # }

        pluralized_category = propositions[0]['category_label'] if propositions[0][
            'category_label'].strip()[-1] == 's' else propositions[0]['category_label'] + 's'
        response = {
            "attachments": [{
                "author_name": provider.title() + " : " + pluralized_category,
                "author_link": frichti_api.FRICHTI_BASE_URL,
                "author_icon": frichti_api.FRICHTI_LOGO
            }]
        }

        attachment_template = {
            "title": "",
            "title_link": "",
            "fields": [
                {
                    # Short description
                    "value": "",
                    "short": False
                }, {
                    # Price
                    "title": "",
                    "short": False
                }
            ],
            "thumb_url": "",
            "color": "#7CD197"
        }

        for proposition in propositions:
            new_attachment = copy.deepcopy(attachment_template)

            new_attachment['title'] = proposition['title']
            new_attachment['title_link'] = frichti_api.get_product_url(proposition[
                                                                       'productId'])
            new_attachment['fields'][0][
                'value'] = proposition['shortDescription']
            new_attachment['fields'][1][
                'title'] = "Prix : " + str(proposition['price']) + " €"
            new_attachment['thumb_url'] = proposition['image']['url']

            response['attachments'].append(new_attachment)

        return response

    def ask(self, provider, query, param1=None):
        response = "Should never happen ----"
        if provider == 'frichti':
            response = ask_frichti(query, param1)
            if query == 'menu_categories':
                response = self.format_menu_categories(provider, response)
            elif query == 'propositions':
                response = self.format_propositions(provider, response)
        return response
