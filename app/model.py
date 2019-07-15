from mongoengine import *


connect('lingua')


class Languages(Document):
    language = StringField(required=True)
    code = StringField(required=True, max_length=3)
    type = StringField(required=True)
    default = BooleanField()


class Sentences(Document):
    text = StringField(required=True)
    lang = ReferenceField(Languages) 


class Users(Document):
    fullname = StringField()
    username = StringField()
    location = StringField()
    avatar = StringField()
