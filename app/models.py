from mongoengine import *
import os
import ast


class Languages(Document):
    language = StringField(required=True)
    code = StringField(required=True, max_length=3, unique=True)
    type = StringField(required=True)
    default = BooleanField(default=False)

    def serialize(self):
        return {
            "name": self.language,
            "code": self.code,
            "type": self.type,
            "default": self.default
        }


class Sentences(Document):
    text = StringField(required=True)
    lang = ReferenceField(Languages)

    def serialize(self):
        return {
            "id": str(self.pk),
            "text": self.text,
            "language": self.lang.serialize()
        }


class Users(Document):
    fullname = StringField()
    username = StringField(unique=True, required=True)
    location = StringField()
    avatar = StringField()

    def serialize(self):
        return {
            "id": str(self.pk),
            "fullname": self.fullname,
            "username": self.username,
            "location": self.location,
            "avatar": self.avatar
        }


class File(EmbeddedDocument):
    name = StringField()
    content = BinaryField()


class Translations(Document):
    author = ReferenceField(Users)
    targetlang = ReferenceField(Languages)
    sentence = ReferenceField(Sentences)
    audiofile = EmbeddedDocumentField(File)

    def serialize(self):
        return {
            "id": str(self.pk),
            "author": self.author.serialize(),
            "target_language": self.targetlang.serialize(),
            "sentence": self.sentence.serialize(),
            "audiofile": self.filename.name
        }
