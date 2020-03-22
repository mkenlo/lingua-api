import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'SuperSecret'
    DB_NAME = os.environ.get('DB_NAME') or "lingua_db"
    DB_USER = os.environ.get('DB_USER') or None
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or None
    DB_HOST = os.environ.get('DB_HOST') or "localhost"
    DB_PORT =  os.environ.get('DB_PORT') or 27017

config = {
    'default': Config,
}
