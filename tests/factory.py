from app.models import *
import json
import sys
import os
sys.path.append("..")


def removeCollections():
    Languages.drop_collection()
    Sentences.drop_collection()


def insertDummyLanguages():
    with open('db/dummy/languages.json') as f:
        data = json.load(f)
        for entry in data:
            Languages(language=entry["language"], code=entry["code"],
                      type=entry["type"], default=entry["default"]).save()


def insertDummySentences():
    insertDummyLanguages()
    lang_fr = Languages.objects(language="francais").first()
    lang_en = Languages.objects(language="english").first()
    lang = lang_fr
    with open('db/dummy/sentences.json') as f:
        data = json.load(f)
        for entry in data:
            if entry["language"] == "francais":
                lang = lang_fr
            if entry["language"] == "english":
                lang = lang_en
            Sentences(lang=lang, text=entry["text"]).save()
