import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))


with open('settings.json') as f:
    settings = json.load(f)
    os.environ["SECRET_KEY"] = settings["secret_key"]
    os.environ["DEV_DATABASE_URL"] = settings["dev_database_url"]
    os.environ["TEST_DATABASE_URL"] = settings["test_database_url"]
    os.environ["DATABASE_URL"] = settings["prod_database_url"]


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'SuperSecret'


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = os.environ.get('DEV_DATABASE_URL')


class TestingConfig(Config):
    TESTING = True
    DATABASE_URI = os.environ.get('TEST_DATABASE_URL')


class ProductionConfig(Config):
    DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
