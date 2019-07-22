from sanic import Blueprint
from sanic import response
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging
from app.models import *
from math import ceil


api = Blueprint('api')
DEFAULT_TOPIC = "audio-recordings"
ITEMS_PER_PAGE = 20


responseError = {"message": "Invalid Payload."}
responseListObjects = {"page": 1, "results": [],
                       "total_results": 0, "total_pages": 0}


@api.route("/")
def index(request):
    return response.json({"message": "welcome to Lingua API"})


@api.route("/languages", methods=["POST"])
def saveLanguages(request):
    if request.method == "POST":
        postdata = request.json
        if "language" not in postdata:
            return response.json(responseError, status=400)
        if "code" not in postdata:
            return response.json(responseError, status=400)
        if "type" not in postdata:
            return response.json(responseError, status=400)
        try:
            new_lang = Languages(
                language=postdata["language"],
                code=postdata["code"],
                type=postdata["type"])
            if "default" in postdata:
                new_lang.default = postdata["default"]
            new_lang.save()
            return response.json({"message": "Added One Item"}, status=201)
        except Exception as err:
            responseError["message"] = str(err)
            return response.json(responseError, status=400)


@api.route("/languages")
def getLanguages(request):
    try:
        languages = Languages.objects()
        args = request.json
        if args:
            if len(args) > 2:
                raise Exception("Expecting less than 3 arguments")
            if "language" in args:
                languages = languages.filter(language=args["language"])
            if "type" in args and "language" in args:
                responseError["message"] = "Cannot filter with both arguments `language` and `type`"
                return response.json(responseError, status=400)
            if "type" in args:
                languages = languages.filter(type=args["type"])
            if "page" in args and int(args["page"]) > 1:
                languages = languages.skip(int(args["page"])*ITEMS_PER_PAGE)
                responseListObjects["page"] = args["page"]

        responseListObjects["total_results"] = languages.count()
        responseListObjects["total_pages"] = ceil(
            languages.count() / ITEMS_PER_PAGE)
        languages.limit(ITEMS_PER_PAGE)
        responseListObjects["results"] = [d.serialize() for d in languages]
        return response.json(responseListObjects)
    except Exception as err:
        responseError["message"] = err
        return response.json(responseError, status=400)


@api.route("/sentences")
def getSentences(request):
    pass


@api.route("/sentences/{id}")
def getSentencesById(request, id):
    pass


@api.route("/sentences/{id}/translations")
def getTranslationsBySentenceId(request, id):
    pass


@api.route("/translations", methods=["GET, POST"])
def getTranslations(request):
    pass


@api.route("/translations/{id}")
def getTranslationsById(request, id):
    pass


@api.route("/users", methods=["POST"])
def getUsers(request):
    pass


@api.route("/users/{id}")
def getUsersById(request):
    pass


@api.route("/users/{id}/translations")
def getTranslationsByUserId(request):
    pass


def kafka_producer(data):
    """ Calling the Broker to process the message"""
    producer = KafkaProducer(bootstrap_servers=['192.168.0.241:9092'])
    # produce asynchronously with callbacks
    # producer.send('test', data).add_callback(on_send_success).add_errback(on_send_error)
    producer.flush()


def on_send_success(record_metadata):
    logging.info(record_metadata.topic)
    logging.info(record_metadata.partition)
    logging.info(record_metadata.offset)


def on_send_error(excp):
    logging.error('I am an errback', exc_info=excp)
    # handle exception
