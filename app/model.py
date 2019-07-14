from mongoengine import *


connect('lingua')


class Languages(Document):
    language = StringField(required=true)
    code = StringField(required=true, max_length=3)
    type = StringField(required=true)
    default = BooleanField()
