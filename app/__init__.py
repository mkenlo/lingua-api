from sanic import Sanic
from app.main import api


def create_app():
    app = Sanic(__name__)
    app.blueprint(api)


    return app