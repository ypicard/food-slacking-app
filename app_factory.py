from flask import Flask
from flask_pymongo import PyMongo
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo = PyMongo()


def create_app():
	app = Flask(__name__)
	# Local settings
	# MONGO_URL = os.environ.get("MONGODB_URI_LOCAL")
	
	# Prod
	MONGO_URL = os.environ.get("MONGODB_URI")
	
	logger.info('Connecting to mongo db : ' + MONGO_URL)
	app.config['MONGO_URI'] =MONGO_URL
	
	mongo.init_app(app)
	return app