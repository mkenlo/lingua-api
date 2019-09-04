import pytest
import json
from .factory import insertDummyLanguages, removeCollections
from app import create_app
from app.models import *
import sys
sys.path.append("..")


@pytest.yield_fixture
def app():
    app = create_app("testing")
    yield app


@pytest.fixture
def test_cli(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))


@pytest.fixture
def preFillDB(request):
    # adding 5 Language documents
    insertDummyLanguages()

    def fin():
        removeCollections()

    request.addfinalizer(fin)


async def test_getLanguages_with_noParam_shouldPass(test_cli, preFillDB):
    resp = await test_cli.get('/languages')
    resp_json = await resp.json()
    assert resp_json["total_results"] == 5
    assert len(resp_json["results"]) == 5
    assert resp_json["page"] == 1
    assert resp_json["results"][0]["name"] == "francais"
    assert resp.status == 200


async def test_getLanguages_with_moreThanExpectedParam_shouldFail(test_cli, preFillDB):
    params = {'page': 2, 'type': 'local', 'not_valid_param': 50}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Expecting less than 3 arguments"
    assert resp.status == 400


async def test_getLanguages_with_bothExpectedParam_shouldPass(test_cli, preFillDB):
    params = {'page': 2, 'type': 'local'}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 200
    assert resp_json["total_results"] == 3
    assert len(resp_json["results"]) == 0
    assert resp_json["page"] == 2


async def test_getLanguages_with_validPageNum_shouldPass(test_cli, preFillDB):
    params = {'page': 20}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 200
    assert resp_json["total_results"] == 5
    assert len(resp_json["results"]) == 0
    assert resp_json["page"] == 20


async def test_getLanguages_with_invalidPageNum_shouldFail(test_cli, preFillDB):
    params = {'page': "test"}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Required Integer, found String"
    assert resp.status == 400


async def test_getLanguages_with_validTypeLanguage_shouldPass(test_cli, preFillDB):
    params = {'type': "foreign"}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 200
    assert resp_json["total_results"] == 2
    assert len(resp_json["results"]) == 2
    assert resp_json["results"][0]["type"] == "foreign"


async def test_addLanguages_with_noParam_shouldFail(test_cli):
    resp = await test_cli.post('/languages')
    resp_json = await resp.json()
    assert resp_json["message"] == "Invalid Payload."
    assert resp.status == 400


async def test_addLanguages_with_unexpectedParam_shouldFail(test_cli):
    params = {"invalid_field": 2, "language": "dummy"}
    resp = await test_cli.post('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 400
    assert resp_json["message"] == "Invalid Payload."


async def test_addLanguages_with_invalidParam_shouldFail(test_cli):
    params = {"language": "dummy_test", "code": "DUMMY", "type": 9}
    resp = await test_cli.post('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 400
    assert resp_json["message"] == "Invalid Field Name or Value"


async def test_addLanguages_with_validParam_shouldPass(test_cli):
    params = {"language": "dummy_test", "code": "DUM", "type": "local"}
    resp = await test_cli.post('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp.status == 201
    assert resp_json["message"] == "Added One Item"
    assert Languages.objects().first().language == "dummy_test"
    assert Languages.objects().first().code == "DUM"
    removeCollections()
