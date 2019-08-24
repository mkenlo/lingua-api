from app.models import *
import json
import sys
import os
sys.path.append("..")


def removeCollections():
    Languages.drop_collection()
    Sentences.drop_collection()
    Translations.drop_collection()
    Users.drop_collection()


def insertDummyLanguages():
    with open('db/dummy/languages.json') as f:
        data = json.load(f)
        for entry in data:
            Languages(language=entry["language"], code=entry["code"],
                      type=entry["type"], default=entry["default"]).save()


def insertDummySentences():
    lang = dict()
    lang["francais"] = Languages.objects(language="francais").first()
    lang["english"] = Languages.objects(language="english").first()
    with open('db/dummy/sentences.json') as f:
        data = json.load(f)
        for entry in data:
            Sentences(lang=lang[entry["language"]], text=entry["text"]).save()


def insertDummyUsers():
    with open('db/dummy/users.json') as f:
        data = json.load(f)
        for entry in data:
            Users(username=entry["username"],
                  fullname=entry["fullname"],
                  location=entry["location"],
                  avatar=entry["avatar"]).save()


def insertDummyTranslations():
    user = Users.objects.first()
    text = Sentences.objects().first()
    lang = Languages.objects(type="local").first()
    audiofiles = ["consectetuer.mov",
                  "faucibusOrciLuctus.avi", "dolor.mp3"]
    for f in audiofiles:
        file = File(name=f, content=f.encode())
        Translations(author=user, targetlang=lang,
                     sentence=text, audiofile=file).save()
