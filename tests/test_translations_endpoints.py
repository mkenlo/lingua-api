import pytest
import json
from pprint import pprint
from .factory import (insertDummyLanguages, insertDummySentences, insertDummyTranslations,
                      insertDummyUsers, removeCollections, )
from app import create_app
from app.models import *
import sys
sys.path.append("..")


NUM_TRANSLATIONS_FROM_TESTSET = 3


@pytest.yield_fixture
def app():
    app = create_app("testing")
    yield app


@pytest.fixture
def test_cli(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))


@pytest.fixture
def preFillDB(request):
    insertDummyLanguages()
    insertDummySentences()
    insertDummyUsers()
    insertDummyTranslations()

    def fin():
        removeCollections()

    request.addfinalizer(fin)


async def test_getTranslations_with_noParam_shouldPass(test_cli, preFillDB):
    resp = await test_cli.get('/translations')
    resp_json = await resp.json()
    assert resp.status == 200
    assert resp_json["page"] == 1
    assert resp_json["total_results"] == NUM_TRANSLATIONS_FROM_TESTSET
    assert resp_json["results"][0]["author"] == "hmyron"
    assert resp_json["results"][1]["audiofile"] == "faucibusOrciLuctus.avi"


async def test_getTranslationsById_with_unKnownID_shouldFailed(test_cli, preFillDB):
    resp = await test_cli.get('/translations/veryunknown')
    resp_json = await resp.json()
    assert resp.status == 404
    assert resp_json["message"] == "Object Not found"


async def test_getTranslations_with_invalidPageNum_shouldFail(test_cli, preFillDB):
    params = {'page': "test"}
    resp = await test_cli.get('/sentences', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Required Integer, found String"
    assert resp.status == 400


async def test_getTranslationsbySentencesID_with_knownID_shouldPass(test_cli, preFillDB):
    phrase = Sentences.objects().first()
    resp = await test_cli.get('/sentences/{}/translations'.format(phrase.pk))
    resp_json = await resp.json()
    assert resp.status == 200
    assert resp_json["page"] == 1
    assert resp_json["total_results"] == NUM_TRANSLATIONS_FROM_TESTSET
    assert resp_json["results"][0]["sentence"] == phrase.text


async def test_addTranslations_with_noParam_shouldFailed(test_cli, preFillDB):
    resp = await test_cli.post('/translations')
    resp_json = await resp.json()
    assert resp_json["message"] == "Invalid Payload."
    assert resp.status == 400


async def test_addTranslations_with_unExpectedParam_shouldFailed(test_cli, preFillDB):
    params = {"target_lang": "test", "unexpectedField": "test",
              "anotherUnExpectedField": "dummy"}
    resp = await test_cli.post('/translations', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Missing or Wrong Arguments"
    assert resp.status == 400


async def test_addTranslations_with_TargetLangEqualSourceLang_shouldFailed(test_cli, preFillDB):
    phrase = Sentences.objects().first()
    params = {
        "author":  Users.objects().first().username,
        "sentence":  str(phrase.pk),
        "target_lang": phrase.lang.language,
        "audiofile":
        {
            "name":  "test.mp3",
            "content": "a0b64dd695877860c37434559104ad5156f8b5f6"
        }
    }
    resp = await test_cli.post('/translations', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Target Language equal Source Language"
    assert resp.status == 400


async def test_addTranslations_with_unknownTargetLang_shouldFailed(test_cli, preFillDB):
    phrase = Sentences.objects().first()
    params = {
        "author":  Users.objects().first().username,
        "sentence":  str(phrase.pk),
        "target_lang": "test",
        "audiofile":
        {
            "name":  "test.mp3",
            "content": "a0b64dd695877860c37434559104ad5156f8b5f6"
        }
    }
    resp = await test_cli.post('/translations', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Trying to reference an unknown object <test>"
    assert resp.status == 400


async def test_addTranslations_with_noFileAttached_shouldFailed(test_cli, preFillDB):
    phrase = Sentences.objects().first()
    params = {
        "author":  Users.objects().first().username,
        "sentence":  str(phrase.pk),
        "target_lang": "test"}
    resp = await test_cli.post('/translations', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Missing or Wrong Arguments"
    assert resp.status == 400


async def test_addTranslations_with_unknownAuthor_shouldFailed(test_cli, preFillDB):
    phrase = Sentences.objects().first()
    params = {
        "author": "unknown",
        "sentence":  str(phrase.pk),
        "target_lang": "english",
        "audiofile":
        {
            "name":  "test.mp3",
            "content": "a0b64dd695877860c37434559104ad5156f8b5f6"
        }
    }
    resp = await test_cli.post('/translations', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Trying to reference an unknown object <unknown>"
    assert resp.status == 400


async def test_addTranslations_with_validParam_shouldPass(test_cli, preFillDB):
    phrase = Sentences.objects().first()
    params = {
        "author":  Users.objects().first().username,
        "sentence":  str(phrase.pk),
        "target_lang": "english",
        "audiofile":
        {
            "name":  "test.mp3",
            "content": "a0b64dd695877860c37434559104ad5156f8b5f6"
        }
    }
    resp = await test_cli.post('/translations', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Added One Item"
    assert resp.status == 200
