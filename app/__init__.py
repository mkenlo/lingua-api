from sanic import Sanic
from app.main import api

from config import config
from mongoengine import connect
import os


def create_app(config_name="default"):
    app = Sanic(__name__)
    app.blueprint(api)

    app.config.from_object(config[config_name])
    app_config = config[config_name]
    connect(db=app_config.DB_NAME, username=app_config.DB_USER, password=app_config.DB_PASSWORD, DB_HOST = app_config.DB_HOST)

    return app
