from mongoengine import *
import os


class Languages(Document):
    language = StringField(required=True)
    code = StringField(required=True, max_length=3, unique=True)
    type = StringField(required=True)
    default = BooleanField(default=False)

    def serialize(self):
        return {
            "language": self.language,
            "code": self.code,
            "type": self.type,
            "default": self.default
        }


class Sentences(Document):
    text = StringField(required=True)
    lang = ReferenceField(Languages)

    def serialize(self):
        return {
            "text": self.language,
            "language": self.lang.seriaize()
        }


class Users(Document):
    fullname = StringField()
    username = StringField(required=True)
    location = StringField()
    avatar = StringField()

    def serialize(self):
        return {
            "fullname": self.fullname,
            "username": self.username,
            "location": self.location,
            "avatar": self.avatar
        }


class Translations(Document):
    author = ReferenceField(Users)
    targetlang = ReferenceField(Languages)
    sentence = ReferenceField(Sentences)
    filename = StringField(required=True)

    def serialize(self):
        return {
            "author": self.author.serialize(),
            "target_language": self.targetlang.serialize(),
            "sentence": self.sentence.serialize(),
            "filename": self.filename
        }
