from app.model import *
import sys
sys.path.append("..")


class TestClassModel(object):
    def test_languages(self):
        """basic test Languages Collection"""
        lang = Languages(language="russian", code="RUS",
                         type="foreign", default=False)
        lang.save()
        assert Languages.objects.count() > 0
        assert isinstance(lang, Languages)

    def test_sentences(self):
        """basic test Sentences Collection"""
        lang = Languages.objects(language="russian").first()
        text = Sentences(text="spasibo", lang=lang)
        text.save()
        assert Sentences.objects.count() > 0
        assert isinstance(text, Sentences)
        assert text.lang.language != "spanish"

    def test_users(self):
        """basic test Users Collection"""
        Users(username="testy").save()
        assert Users.objects().first().username == "testy"

    def test_translations(self):
        """basic test Translations Collection"""
        user = Users.objects().first()
        lang = Languages.objects().first()
        text = Sentences.objects().first()
        Translations(author=user, targetlang=lang,
                     sentence=text, file="myFile.3gp").save()
        assert Translations.objects().first().author.username == "testy"
