# -*- coding: utf-8 -*-

import os
from slackclient import SlackClient
from flask import jsonify
import json
from app_factory import mongo
from pprint import pprint
import frichti_api
import nestor_api
import popchef_api
import pickles_api
import urllib
import utils
import copy
import logging
from random import shuffle


# Instantiate logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROVIDER_CHOICES = [{
    'tag': 'frichti',
    'name': 'Frichti',
    'color': '#f7e77a',
    'has_api': True,
    'message': 'Voir le menu !',
    'thumb_url': frichti_api.FRICHTI_LOGO
},
#     {
#     'tag': 'popchef',
#     'name': 'Popchef',
#     'color': '#1ec28e',
#     'has_api': True,
#     'message': 'Voir le menu !',
#     'thumb_url': popchef_api.POPCHEF_LOGO
# },
    {
    'tag': 'ubereats',
    'name': 'UberEats',
    'color': '#1c95a5',
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
    'thumb_url': pickles_api.PICKLES_LOGO
},
    {
    'tag': 'nestor',
    'name': 'Nestor',
    'color': '#ef6537',
    'has_api': True,
    'website_url': "https://www.nestorparis.com/",
    'message': 'Montre moi le menu !',
    'thumb_url': nestor_api.NESTOR_LOGO
}]

# TODO : Ajouter un boutton pour revenir en arriere a chaque etape
# TODO : Understand kitchen id in frichti api


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
        pprint(auth_response)
        logging.info("Saving new credentials to database :\n  - team_id: " +
                     auth_response["team_id"] + "\n  - team_name: " + auth_response["team_name"])
        mongo.db.credentials.update({
            'team_id': auth_response["team_id"]
        }, {
            '$set': {'team_id': auth_response["team_id"],
                     'team_name': auth_response["team_name"],
                     'access_token': auth_response["access_token"],
                     'bot_id':  auth_response["bot"]["bot_user_id"],
                     'bot_token': auth_response["bot"]["bot_access_token"]
                     }
        }, True)

        # Reconnect the Slack Client with the correct bot token
        self.client = SlackClient(auth_response["bot"]["bot_access_token"])

    def authToCorrectTeam(self, team_id):
        team_credentials = mongo.db.credentials.find_one({'team_id': team_id})
        logger.info("Connecting slack client to :\n  - team_name: " + team_credentials['team_name'] + "\n  - team_id: " +
                    team_id)
        self.client = SlackClient(team_credentials['bot_token'])
        self.id = team_credentials['bot_id']

    def getAtBot(self):
        return '<@' + self.id + '>'

    def display_providers(self, team, channel):
        logger.info("postMessage : display provider selection buttons")

        text = "Chez qui voulez-vous commander aujourd'hui ?"

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

        self.client.api_call("chat.postMessage", token=team, channel=channel,
                             text=text,
                             attachments=attachments,
                             as_user=True)

    def post_message(self, team, channel, message):
        logger.info("postMessage : " + message)

        self.client.api_call("chat.postMessage", token=team,
                             channel=channel, text=message, as_user=True)

    def format_menu_categories(self, provider, categories):
        # Returns a replacement response to replace the active Slack message,
        # and 'other_responses' which will appear as new messages

        # TODO : Define a model structure for categories param

        provider_URLS = self.get_provider_URLS(provider)
        if not categories:
            # If not categories available for this day (holidays for example)
            response = {
                'attachments': [{
                    'text': "Aucune catégorie disponible aujourd'hui ! Retentez votre chance demain :)",
                            "author_name": provider.title(),
                            "author_link": provider_URLS['BASE_URL'],
                            "author_icon": provider_URLS['LOGO_URL']
                }]
            }
            return response

        response = {
            'text': 'Choisissez une catégorie pour connaitre ses choix :',
            'attachments': [{
                "author_name": provider.title(),
                "author_link": provider_URLS['BASE_URL'],
                "author_icon": provider_URLS['LOGO_URL']
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

            if (idx + 1) % 5 == 0:
                response['attachments'].append(new_attachment)
                new_attachment = copy.deepcopy(attachment_template)
        response['attachments'].append(new_attachment)
        return response

    def format_propositions(self, provider, propositions):
        # Returns a replacement response to replace the active Slack message,
        # and 'other_responses' which will appear as new messages

        # TODO : Define a model structure for propositions param

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

        provider_URLS = self.get_provider_URLS(provider)

        # If not proposition in the selected category
        if not propositions:
            response = {
                'attachments': [{
                    'text': "Rien à manger ici aujourd'hui ! Retentez votre chance demain :)",
                            "author_name": provider.title(),
                            "author_link": provider_URLS['BASE_URL'],
                            "author_icon": provider_URLS['LOGO_URL']
                }]
            }
            return response


        if propositions[0]['category_label'].strip()[-1] in ['s', '!', ')']:
            pluralized_category = propositions[0]['category_label']
        else:
            pluralized_category = propositions[0]['category_label'] + 's'

        response = {
            "attachments": [{
                "author_name": provider.title() + " : " + pluralized_category,
                "author_link": provider_URLS['BASE_URL'],
                "author_icon": provider_URLS['LOGO_URL']
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
            "color": None
        }

        for proposition in propositions:
            new_attachment = copy.deepcopy(attachment_template)
            new_attachment['title'] = proposition['title']
            new_attachment[
                'title_link'] = provider_URLS['PRODUCT_BASE_URL'] + proposition['productId']
            new_attachment['fields'][0][
                'value'] = proposition['shortDescription']
            if proposition['price']:
                new_attachment['fields'][1][
                    'title'] = ("Prix : " + str(proposition['price']) + " €")
            if provider == 'nestor':
                new_attachment['fields'][1]['title'] += " (Menu complet)"
            new_attachment['thumb_url'] = proposition['image']['url']
            new_attachment['color'] = utils.random_color()

            response['attachments'].append(new_attachment)

        return response

    def get_provider_URLS(self, provider):
        # Used to get useful base urls for each provider
        if provider == 'frichti':
            return {
                "BASE_URL": frichti_api.FRICHTI_BASE_URL,
                "LOGO_URL": frichti_api.FRICHTI_LOGO,
                "PRODUCT_BASE_URL": frichti_api.FRICHTI_BASE_URL + '/p/'
            }
        elif provider == 'popchef':
            return {
                "BASE_URL": popchef_api.POPCHEF_BASE_URL,
                "LOGO_URL": popchef_api.POPCHEF_LOGO,
                "PRODUCT_BASE_URL": popchef_api.POPCHEF_BASE_URL + '/p/'
            }
        elif provider == 'pickles':
            return {
                "BASE_URL": pickles_api.PICKLES_BASE_URL,
                "LOGO_URL": pickles_api.PICKLES_LOGO,
                "PRODUCT_BASE_URL": pickles_api.PICKLES_BASE_URL
            }
        elif provider == 'nestor':
            return {
                "BASE_URL": nestor_api.NESTOR_BASE_URL,
                "LOGO_URL": nestor_api.NESTOR_LOGO,
                "PRODUCT_BASE_URL": nestor_api.NESTOR_BASE_URL
            }

    def ask(self, provider, query, param1=None):
        response = "Should never happen !"
        if provider == 'frichti':
            response = frichti_api.ask_frichti(query, param1)
            if query == 'menu_categories':
                logging.info("postMessage: menu_categories for " + provider)
                response = self.format_menu_categories(provider, response)
            elif query == 'propositions':
                logging.info("postMessage: propositions for " + provider)
                response = self.format_propositions(provider, response)

        elif provider == 'popchef':
            response = popchef_api.ask_popchef(query, param1)
            if query == 'menu_categories':
                logging.info("postMessage: menu_categories for " + provider)
                response = self.format_menu_categories(provider, response)
            elif query == 'propositions':
                logging.info("postMessage: propositions for " + provider)
                response = self.format_propositions(provider, response)

        elif provider == 'pickles':
            response = pickles_api.ask_pickles(query, 'only_category')
            if query == 'menu_categories':
                logging.info("postMessage: propositions for " + provider)
                response = self.format_propositions(provider, response)

        elif provider == 'nestor':
            response = nestor_api.ask_nestor(query, 'only_category')
            if query == 'menu_categories':
                logging.info("postMessage: propositions for " + provider)
                response = self.format_propositions(provider, response)

        return response
