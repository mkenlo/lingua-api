from app.models import *
import json
import sys
import os
sys.path.append("..")


def removeCollections():
    Languages.drop_collection()


def insertDummyLanguages():
    with open('db/dummy/languages.json') as f:
        data = json.load(f)
        for entry in data:
            Languages(language=entry["language"], code=entry["code"],
                      type=entry["type"], default=entry["default"]).save()
