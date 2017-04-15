from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()


def create_app():
	app = Flask(__name__)
	mongo.init_app(app)
	return app