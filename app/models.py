from mongoengine import *
import datetime


class Languages(Document):
    language = StringField(required=True)
    code = StringField(required=True, max_length=3, unique=True)
    type = StringField(required=True)
    default = BooleanField(default=False)

    def serialize(self):
        return {
            "id": str(self.pk),
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
    recordeddate = DateTimeField(default=datetime.datetime.utcnow)

    def serialize(self):
        return {
            "id": str(self.pk),
            "author": self.author.username,
            "language": {
                "from": self.sentence.lang.language,
                "to": self.targetlang.language},
            "sentence": self.sentence.text,
            "audiofile": self.audiofile.name,
            "recordeddate": self.recordeddate.strftime("%b %d, %Y")
        }
