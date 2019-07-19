
from mongoengine import connect, disconnect
from config import config
from app import create_app
import os


class BaseTest(object):

    def create_app(self):
        app.config.from_object(config["testing"])
        return app

    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the class.
        """
        disconnect()
        connect(db=os.environ["TEST_DATABASE_URL"])

    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        db = connect(db=os.environ["TEST_DATABASE_URL"])
        db.drop_database(os.environ["TEST_DATABASE_URL"])
        disconnect()
