# -*- coding: utf-8 -*-
import json
import bot
import os
from app_factory import *
import json
from pprint import pprint
from flask import request, make_response, render_template, jsonify
import urlparse
import frichti_api
import logging

# Instantiate logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

food_slacking_bot = bot.FoodSlackingBot()
app = create_app()


def _event_handler(event_type, slack_event):
    # A helper function that routes events from Slack to our Bot by event type
    # and subtype.
    team = slack_event["team_id"]
    food_slacking_bot.authToCorrectTeam(team)
    
    # ================ Message Events =============== #
    if event_type == "message" and 'text' in slack_event['event']:
        instructions = slack_event['event']['text'].split(' ')

        if not 'bot_id' in slack_event['event']: # Don't allow the bot to respond to itself

            if food_slacking_bot.getAtBot() in instructions and 'help' in instructions: # If help specifically requested
                channel = slack_event['event']['channel']
                message = "If you feel lost, don't panic :bomb: ! Just mention my name and let the magic happen :tophat:\n\nIf you'd like to learn more about me, go see my creator's homepage right here --> https://food-slacking.herokuapp.com :squirrel:\nAnd most importantly, don't hesitate to send him some support ! He looks like a nice guy after all... :frog:"
                food_slacking_bot.post_message(team, channel, message)
                return make_response("Food Slacking Bot posting message", 200)

            elif food_slacking_bot.getAtBot() in instructions: # Post food providers in every other cases
                channel = slack_event['event']['channel']
                food_slacking_bot.display_providers(team, channel)
                return make_response("Food Slacking Bot handling command", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def home():
    """This route renders the installation page with 'Add to Slack' button."""
    # Since we've set the client ID and scope on our Bot object, we can change
    # them more easily while we're developing our app.

    client_id = food_slacking_bot.oauth["client_id"]
    scope = food_slacking_bot.oauth["scope"]
    return render_template("home.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    """
    This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    code_arg = request.args.get('code')
    # The bot's auth method to handles exchanging the code for an OAuth token
    food_slacking_bot.auth(code_arg)
    return render_template("thanks.html")


@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.data)

    # ============= Slack URL Verification ============ #
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    # ============ Slack Token Verification =========== #
    if os.environ.get("VERIFICATION_TOKEN") != slack_event.get("token"):
        message = "Invalid Slack verification token"
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route('/reacts', methods=['GET', 'POST'])
def reacts():
    payload = json.loads(urlparse.parse_qs(request.get_data())['payload'][0])
    team_id = payload['team']['id']
    channel_id = payload['channel']['id']
    callback_id = payload['callback_id']
    actions = payload['actions']

    logging.info("/reacts with :\n  -callback_id=" +
                 callback_id + "\n  -value=" + actions[0]['value'])

    # Rethink this process
    if callback_id == 'food_provider_selection':
        food_provider_choice = actions[0]['value']
        response = food_slacking_bot.ask(
            food_provider_choice, 'menu_categories')
    elif callback_id == 'menu_category_selection':
        provider, category = actions[0]['value'].split('/')
        response = food_slacking_bot.ask(provider, 'propositions', category)

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
