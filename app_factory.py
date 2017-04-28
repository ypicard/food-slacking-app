from flask import Flask
from flask_pymongo import PyMongo
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo = PyMongo()


def create_app():
	app = Flask(__name__)

	# Log settings here :
	logger.info("Current env variables :")
	logger.info("  - CLIENT_ID : " + os.environ.get("CLIENT_ID"))
	logger.info("  - CLIENT_SECRET : " + os.environ.get("CLIENT_SECRET"))
	logger.info("  - VERIFICATION_TOKEN : " + os.environ.get("VERIFICATION_TOKEN"))
	logger.info("  - MONGODB_URI : " + os.environ.get("MONGODB_URI"))
	logger.info("  - APP_BASE_URL : " + os.environ.get("APP_BASE_URL"))

	app.config['MONGO_URI'] = os.environ.get("MONGODB_URI")
	
	mongo.init_app(app)
	return app
