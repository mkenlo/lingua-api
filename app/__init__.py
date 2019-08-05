from sanic import Sanic
from app.main import api

from config import config
from mongoengine import connect
import os


def create_app(config_name="default"):
    app = Sanic(__name__)
    app.blueprint(api)

    app.config.from_object(config[config_name])
    connect(db=config[config_name].DATABASE_URI)

    return app
