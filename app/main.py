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
    return response.json({"message": "Hey, Hello! You did GREAT!"})


@api.route("/languages")
def get_languages(request):
    """
    Return all languages
    Endpoint example: /languages
    No PARAMETERS
    """
    data = my_db.languages.find()
    languages = []
    for d in data:
        d['_id'] = str(d['_id'])
        languages.append(d)
    return response.json({"message": "All languages", "data": languages})


@api.route("/sentences")
def get_sentences_per_lang(request):
    """
    Endpoint example: /sentences?lang=fra
    Query Parameter: lang
    """
    if len(request.args) == 0:
        return response.json({"message": "invalid payload"})
    lang = request.args["lang"][0]
    data = []
    if len(lang) > 0:
        for d in my_db.sentences.find({"lang": lang}):
            d['_id'] = str(d)
            data.append(d)
            print(data)
    else:
        data = my_db.sentences.find_one({"_id": 0})
    # data['_id'] = str(data['_id'])
    return response.json({"message": "sentences from given language", "data": data})


@api.route("/language/<lang_code>")
def get_single_language(request, lang_code):
    """
    PURPOSE: Return a single language object
    PARAMETERS TYPE: query parameter
    Request  parameters:
            code :  the  code of the language  (Usually THREE letters words)
    ENdpoint Example: /language?code=FRA
    """
    # lang_code = request.args['code'][0]
    data = my_db.languages.find_one({"code": lang_code.upper()})
    data['_id'] = str(data['_id'])
    return response.json({"message": "single language", "data": data})

    """    if len(request.args) == 0:
        return response.json({"message": "invalid payload"})
    else:
        # lang_code = request.args['code'][0]
        data = my_db.languages.find_one({"code": lang_code.upper()})
        data['_id'] = str(data['_id'])
        return response.json({"message": "single language", "data": data}) """


@api.route("/sentence", methods=["POST"])
def add_sentence(request):
    """add a new sentence to translate
    Request Parameters: array of language objects
    {
        "language" : the language in which the sentence is written,
        "text": sentence to add
    }

    """
    req = request.json
    my_db.sentences.insert_many(req)
    return response.json({"received": True, "message": "insert successfull", "data": req})


@api.route("/track", methods=["POST"])
def save_track(request):
    """
        save a single audio recording

        request Parameters:
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


@api.route("/multitracks", methods=["POST"])
def save_multitracks(request):
    """
        save multiple audios recording
    """
    data = request.get_response.json() or {}
    res = {"message": "Hello, I got your audio file. Will Process it soon"}
    return response.json(res)


@api.route("/mytranslations", methods=["POST"])
def get_user_translations(request):
    """
    Return all translations for a given users
    """


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


@api.route("/test_request_args")
async def test_request_args(request):
    return response.json({
        "parsed": True,
        "url": request.url,
        "query_string": request.query_string,
        "args": request.args,
        "raw_args": request.raw_args,
        "query_args": request.query_args,
    })


@api.route("/json", methods=["POST"])
def post_json(request):
    return response.json({"received": True, "message": request.json})
