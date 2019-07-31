from sanic import Blueprint
from sanic import response
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging
from app.models import *
from math import ceil
import json

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
        requiredFields = ["language", "code", "type", "default"]
        if not set(requiredFields) >= set(postdata):
            return response.json(responseError, status=400)
        try:
            newLang = Languages(
                language=postdata["language"],
                code=postdata["code"],
                type=postdata["type"])
            if "default" in postdata:
                newLang.default = postdata["default"]
            newLang.save()
            return response.json({"message": "Added One Item"}, status=201)
        except Exception as err:
            responseError["message"] = str(err)
            return response.json(responseError, status=400)


@api.route("/languages")
def getLanguages(request):
    """
    Return all Languages objects
    Parameters in Request body
    {
        "page" : (int)  [Optional, default is 1]
    }
    """
    try:
        languages = Languages.objects()
        args = request.json
        if args:
            if len(args) > 2:
                raise Exception("Expecting less than 3 arguments")
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


@api.route("/languages/<id>")
def getLanguagesById(request, id):
    try:
        return response.json(Languages.objects().with_id(id).serialize())
    except Exception:
        return response.json({"message": "Object Not found"}, status=404)


@api.route("/sentences")
def getSentences(request):
    """
    Return all Sentences objects
    Parameters in Request body
    {
        "page": (int)[Optional, default is 1]
    }
    """
    try:
        sentences = Sentences.objects()
        if request.json:
            if "language" in request.json:
                language = Languages.objects(
                    language=request.json["language"]).first()
                sentences = sentences.filter(lang=language)
            if "page" in request.json and int(request.json["page"]) > 1:
                sentences = sentences.skip(
                    int(request.json["page"])*ITEMS_PER_PAGE)
                responseListObjects["page"] = request.json["page"]

        responseListObjects["total_results"] = sentences.count()
        responseListObjects["total_pages"] = ceil(
            sentences.count() / ITEMS_PER_PAGE)
        sentences.limit(ITEMS_PER_PAGE)
        responseListObjects["results"] = [d.serialize() for d in sentences]
        return response.json(responseListObjects)
    except Exception as err:
        responseError['message'] = str(err)
        return response.json(responseError, status=400)


@api.route("/sentences", methods=["POST"])
def saveSentences(request):
    try:
        if request.json:
            postdata = request.json
            requiredFields = ["text", "language"]
            if not set(requiredFields) >= set(postdata):
                raise AttributeError(
                    "Invalid Payload. Wrong or Missing Attributes")
            if not isinstance(postdata["text"], str):
                raise TypeError("<text> field must be a string")

            newSentence = Sentences(text=postdata["text"])
            language = Languages.objects().filter(
                language=postdata["language"]).first()
            if not language:
                raise ValueError(
                    "No language <{}> found".format(postdata["language"]))
            newSentence.lang = language
            newSentence.save()
            return response.json({"message": "Added One item"})
        else:
            raise ValueError("Invalid Payload. No Post Data Found")
    except Exception as err:
        return response.json(str(err), status=400)


@api.route("/sentences/<id>")
def getSentencesById(request, id):
    try:
        return response.json(Sentences.objects().with_id(id).serialize())
    except Exception:
        return response.json({"message": "Object Not found"}, status=404)


@api.route("/sentences/<id>/translations")
def getTranslationsBySentenceId(request, id):
    try:
        sentence = Sentences.objects().with_id(id)
        translations = Translations.objects().filter(sentence=sentence)
        args = request.json
        if args:
            if "page" in args and int(args["page"]) > 1:
                translations = translations.skip(
                    int(args["page"])*ITEMS_PER_PAGE)
                responseListObjects["page"] = args["page"]

        responseListObjects["total_results"] = translations.count()
        responseListObjects["total_pages"] = ceil(
            translations.count() / ITEMS_PER_PAGE)
        responseListObjects["results"] = [d.serialize() for d in translations]
        return response.json(responseListObjects)
    except Exception:
        return response.json({"message": "Object Not found"}, status=404)


@api.route("/translations")
def getTranslations(request):
    """"
    Return all translations objects
    Parameters in Request body
    {
        "page": (int)[Optional, default is 1]
    }
    """
    try:
        translations = Translations.objects()
        args = request.json
        if args:
            if "page" in args and int(args["page"]) > 1:
                translations = translations.skip(
                    int(args["page"])*ITEMS_PER_PAGE)
                responseListObjects["page"] = args["page"]

        responseListObjects["total_results"] = translations.count()
        responseListObjects["total_pages"] = ceil(
            translations.count() / ITEMS_PER_PAGE)
        responseListObjects["results"] = [d.serialize() for d in translations]
        return response.json(responseListObjects)
    except Exception as err:
        return response.json({"message": str(err)}, status=400)


@api.route("/translations", methods=["POST"])
def saveTranslations(request):
    """
    Save a new Translation Document
    request Parameters:
        {
            "sentence":  (string) "ID of the sentence to translate",
            target_lang: (string) "target language",
            "audiofile:  (object)
            {
                "name":  (string) "audio file name",
                "content: (bytes or Base64 String) "file content"
            }
        }
    """
    try:
        postdata = request.json
        if not postdata:
            raise ValueError("Missing Post Data")
        requiredFields = ["author", "target_lang", "sentence", "audiofile"]
        if not set(requiredFields) >= set(postdata):
            raise AttributeError("Missing or Wrong Arguments")
        # checking reference fields
        lang = Languages.objects().filter(
            language=postdata["target_lang"]).first()
        author = Users.objects().filter(username=postdata["author"]).first()
        sentence = Sentences.objects().with_id(postdata["sentence"])
        if not lang or not author or not sentence:
            raise Exception("One or More items not Found")

        audioFile = File(
            name=postdata["audiofile"]["name"],
            # encode the string into bytes
            content=postdata["audiofile"]["content"].encode())
        Translations(author=author, targetlang=lang,
                     sentence=sentence, audiofile=audioFile).save()

        # TODO Call Kafka Producer Here
        # data to process {audioFile}

        return response.json({"message": "Added One item"})
    except Exception as err:
        return response.json({"message": str(err)}, status=400)


@api.route("/translations/<id>")
def getTranslationsById(request, id):
    try:
        return response.json(Translations.objects().with_id(id).serialize())
    except Exception:
        return response.json({"message": "Object Not found"}, status=404)


@api.route("/users")
def getUsers(request):
    try:
        users = Users.objects()
        args = request.json
        if args:
            if "page" in args and int(args["page"]) > 1:
                users = users.skip(
                    int(args["page"])*ITEMS_PER_PAGE)
                responseListObjects["page"] = args["page"]

        responseListObjects["total_results"] = users.count()
        responseListObjects["total_pages"] = ceil(
            users.count() / ITEMS_PER_PAGE)
        responseListObjects["results"] = [d.serialize() for d in users]
        return response.json(responseListObjects)
    except Exception:
        return response.json(responseError, status=400)


@api.route("/users", methods=["POST"])
def saveUsers(request):
    try:
        postdata = request.json
        if not postdata:
            raise ValueError("Missing Post Data")
        if "username" not in postdata:
            raise AttributeError("Missing required <username> field")
        user = Users(username=postdata["username"])
        if "fullname" in postdata:
            user.fullname = postdata["fullname"]
        if "location" in postdata:
            user.location = postdata["location"]
        if "avatar" in postdata:
            user.avatar = postdata["avatar"]
        user.save()
        return response.json({"message": "Added one item"})
    except Exception as err:
        return response.json({"message": str(err)}, status=400)


@api.route("/users/<id>")
def getUsersById(request, id):
    try:
        return response.json(Users.objects().with_id(id).serialize())
    except Exception:
        return response.json({"message": "Object Not found"}, status=404)


@api.route("/users/<id>/translations")
def getTranslationsByUserId(request, id):
    try:
        user = Users.objects().with_id(id)
        translations = Translations.objects().filter(author=user)
        args = request.json
        if args:
            if "page" in args and int(args["page"]) > 1:
                translations = translations.skip(
                    int(args["page"])*ITEMS_PER_PAGE)
                responseListObjects["page"] = args["page"]

        responseListObjects["total_results"] = translations.count()
        responseListObjects["total_pages"] = ceil(
            translations.count() / ITEMS_PER_PAGE)
        responseListObjects["results"] = [d.serialize() for d in translations]
        return response.json(responseListObjects)
    except Exception:
        return response.json({"message": "Object Not found"}, status=404)


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
