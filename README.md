# FOOD SLACKING

[![N|Solid](https://platform.slack-edge.com/img/add_to_slack@2x.png)](https://slack.com/oauth/authorize?&client_id=158493540211.158495716179&scope=bot)

Website : https://food-slacking.herokuapp.com

I created this simple slack app/bot to get a daily reminder to check what's for lunch on the different food providers' websites.

At the moment, the supported providers are :
  - Frichti
  - Popchef
  - Uber Eats
  - Deliveroo
  - Foodora 
  - Pickles
  - Nestor

New ones will come quickly, be assured :)

# INSTALLATION
Just follow the instructions provided by the **Add to Slack** button : 
[![N|Solid](https://platform.slack-edge.com/img/add_to_slack.png)](https://slack.com/oauth/authorize?&client_id=158493540211.158495716179&scope=bot)

# SCREENSHOTS
![Screenshot 1](/images/readme-providers.png?raw=true "Choose your daily food provider !")
![Screenshot 2](/images/readme-propositions.png?raw=true "Frichti example : propositions for the 'Plats' category")

# New Features & Updates

  - **May 1st 2017** : First "official" release, with basic functionnalities (only Frichti supported, and a daily task called everyday)
  - **May 2nd 2017** : Add Popchef support
  - **May 6th 2017** : Add UberEats, Deliveroo, Foodora (and more generally, add support for non-api based providers)
  - **May 7th 2017** : Build a nice website with a nice UI : https://food-slacking.herokuapp.com
  - **May 11th 2017** : Add Pickles support
  - **May 17th 2017** : Add Nestor support - Temporarily hide Pickles (they remodelled their whole website...)
  - **May 18th 2017** : Fix Pickles support - Add daily task to fetch and save all menus at 5am
  - **Jan 25th 2018** : Fix Frichti & Pickles support, and removed Popchef because they finally added a security token to their API calls. Oh well. Also removed only restaurant food delivery services for better clarity.

### Development

If you want to help me grow this bot, ping me and I'll do a quick guide on how to set up the app in a local environment !

### Todos

 - Add a return button in each menu
 - Add Chaud chaud chaud, FoodCheri
 - Move send_daily_notifications.py up one level and make it use the bot script to post
 - Fix Popchef support by using scrapping instead of their old API, now protected

License
----

MIT

**Free Software :)**
