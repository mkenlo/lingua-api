from sanic import Blueprint
from sanic import response
from kafka import KafkaProducer
from kafka.errors import KafkaError
from pymongo import MongoClient
import json
import logging


api = Blueprint('api')
DEFAULT_TOPIC = "audio-recordings"

client = MongoClient('mongodb://localhost:27017/')

my_db = client.linguadb


@api.route("/")
def index(request):
    return response.json({"message": "welcome to Lingua API"})


@api.route("/languages")
def get_languages(request):
    """
    Return all languages
    Endpoint example: /languages
    if query parameters are given, the endpoint will return that specific object
    Example:  /languages?code=FRA
    Parameter Name: code
    """
    queryfilter = {}
    if len(request.args) != 0:
        if "code" not in request.args:
            return response.json({"message": "invalid query parameters "})
        else:
            queryfilter["code"] = request.args["code"][0]

    languages = []
    for d in my_db.languages.find(queryfilter):
        d['_id'] = str(d['_id'])
        languages.append(d)
    return response.json({"message": "successfull", "data": languages})


@api.route("/sentences")
def get_sentences(request):
    """
    return all sentences. If a parameter is given, then all sentences from that language
    are returned
    Endpoint example: /sentences?lang=fra
    Query Parameter: (optional) lang 
    """
    queryfilter = {}
    if len(request.args) != 0:
        if "lang" not in request.args:
            return response.json({"message": "invalid query parameters "})
        else:
            queryfilter["lang"] = request.args["lang"][0]
    sentences = []
    for d in my_db.sentences.find(queryfilter):
        d['_id'] = str(d)
        sentences.append(d)

    return response.json({"message": "successfull", "data": sentences})


@api.route("/sentence", methods=["POST"])
def add_sentences(request):
    """add a or multiple new sentences to translate
    Request Parameters: array of language objects
    {
        "language" : the language in which the sentence is written,
        "text": sentence to add
    }
     @TODO : Some sanity check need to be done on POST DATA
    """
    req = request.json
    my_db.sentences.insert_many(req)
    return response.json({"message": "successfull", "data": req})


@api.route("/tracks", methods=["POST"])
def save_track(request):
    """
        save one or many audio recordings

        request Parameters: array of recording objects
        {
            "text": "the sentence to translate",
            language: {
                "from": "the language in which the sentence is written",
                "to": "the language in which the audio file is recorded"
            },
            "audioFile: "the translated audio recording of `text`"
        }

        @TODO : Some sanity check need to be done on POST DATA
    """
    data = request.body
    # Calling Kafka Producer
    kafka_producer(data)
    res = {"message": "Hello, I got your audio file. Will Process it soon", "data": data}
    return response.json(res)


@api.route("/mytranslations", methods=["POST"])
def get_user_translations(request):
    """
    Return all translations for a given users
    """
    return response.json({"message": "200 successfull"})


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
