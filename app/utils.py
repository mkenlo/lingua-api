from app.models import *


def validate_translations_input(input):
    if not input:
        raise ValueError("Invalid Payload.")
    requiredFields = ["author", "target_lang", "sentence", "audiofile"]
    if not (set(input) >= set(requiredFields)):
        raise AttributeError("Missing or Wrong Arguments")
    # checking reference fieldMissing or Wrong Argumentss
    lang = Languages.objects().filter(
        language=input["target_lang"]).first()
    author = Users.objects().filter(username=input["author"]).first()
    sentence = Sentences.objects().with_id(input["sentence"])
    if not lang:
        raise Exception(
            "Trying to reference an unknown object <{}>".format(input["target_lang"]))
    if not author:
        raise Exception(
            "Trying to reference an unknown object <{}>".format(input["author"]))
    if not sentence:
        raise Exception(
            "Trying to reference an unknown object <{}>".format(input["sentence"]))
    if lang == sentence.lang:
        raise Exception("Target Language equal Source Language")

    input["target_lang"] = lang
    input["author"] = author
    input["sentence"] = sentence
    return input
