import pytest
import json
from .factory import insertDummySentences, removeCollections
from app import create_app
from app.models import *
import sys
sys.path.append("..")


NUM_TOTAL_SENTENCES = 10
NUM_SENTENCES_OF_LANG_FRANCAIS = 6
FIRST_SENTENCE_LANG = "francais"


@pytest.yield_fixture
def app():
    app = create_app("testing")
    yield app


@pytest.fixture
def test_cli(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))


@pytest.fixture
def generateData(request):
    # adding dummy sentences
    insertDummySentences()

    def fin():
        removeCollections()

    request.addfinalizer(fin)


async def test_getSentences_with_noParam_shouldPass(test_cli, generateData):
    resp = await test_cli.get('/sentences')
    resp_json = await resp.json()
    assert resp_json["total_results"] == NUM_TOTAL_SENTENCES
    assert len(resp_json["results"]) == NUM_TOTAL_SENTENCES
    assert resp_json["page"] == 1
    assert resp_json["results"][0]["language"]["name"] == FIRST_SENTENCE_LANG
    assert resp.status == 200


async def test_getSentencesById_with_unKnownID_shouldFailed(test_cli, generateData):
    resp = await test_cli.get('/sentences/veryunknown')
    resp_json = await resp.json()
    assert resp.status == 404
    assert resp_json["message"] == "Object Not found"


async def test_getSentences_with_bothExpectedParam_shouldPass(test_cli, generateData):
    params = {'page': 2, 'language': 'francais'}
    resp = await test_cli.get('/sentences', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 200
    assert resp_json["total_results"] == NUM_SENTENCES_OF_LANG_FRANCAIS
    assert len(resp_json["results"]) == 0
    assert resp_json["page"] == 2


async def test_getSentences_with_validPageNum_shouldPass(test_cli, generateData):
    params = {'page': 20}
    resp = await test_cli.get('/sentences', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 200
    assert resp_json["total_results"] == NUM_TOTAL_SENTENCES
    assert len(resp_json["results"]) == 0
    assert resp_json["page"] == 20


async def test_getSentences_with_invalidPageNum_shouldFail(test_cli, generateData):
    params = {'page': "test"}
    resp = await test_cli.get('/sentences', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Required Integer, found String"
    assert resp.status == 400


async def test_getSentences_with_validLanguage_shouldPass(test_cli, generateData):
    params = {'language': "francais"}
    resp = await test_cli.get('/sentences', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 200
    assert resp_json["total_results"] == 6
    assert len(resp_json["results"]) == 6
    assert resp_json["results"][0]["language"]["name"] == FIRST_SENTENCE_LANG


async def test_addSentences_with_noParam_shouldFail(test_cli):
    resp = await test_cli.post('/sentences')
    resp_json = await resp.json()
    assert resp_json["message"] == "Invalid Payload."
    assert resp.status == 400


async def test_addSentences_with_unexpectedParam_shouldFail(test_cli):
    params = {"invalid_field": 2, "language": "dummy"}
    resp = await test_cli.post('/sentences', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 400
    assert resp_json["message"] == "Invalid Payload."


async def test_addSentences_with_invalidTextParam_shouldFail(test_cli):
    params = {"language": "francais", "text": 9}
    resp = await test_cli.post('/sentences', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 400
    assert resp_json["message"] == "<text> field must be a string"


async def test_addSentences_with_unknownLanguageParam_shouldFail(test_cli):
    params = {"language": "francais", "text": "dummy text"}
    resp = await test_cli.post('/sentences', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 404
    assert resp_json["message"] == "No language <francais> found"


async def test_addSentences_with_validParam_shouldPass(test_cli):
    Languages(language="test", code="TES", type="foreign").save()
    params = {"language": "test", "text": "dummy text"}
    resp = await test_cli.post('/sentences', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 201
    assert resp_json["message"] == "Added One Item"
    assert Sentences.objects().first().lang.language == "test"
    assert Sentences.objects().first().text == "dummy text"
    removeCollections()
