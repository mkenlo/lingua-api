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
def generateData(request):
    # adding 5 Language documents
    insertDummyLanguages()

    def fin():
        removeCollections()

    request.addfinalizer(fin)


async def test_getLanguages_with_noParam_shouldPass(test_cli, generateData):
    resp = await test_cli.get('/languages')
    resp_json = await resp.json()
    assert resp_json["total_results"] == 5
    assert len(resp_json["results"]) == 5
    assert resp_json["page"] == 1
    assert resp.status == 200


async def test_getLanguages_with_moreThanExpectedParam_shouldShowErrorMsg(test_cli, generateData):
    params = {'page': 2, 'type': 'local', 'no_valid_param': 50}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Expecting less than 3 arguments"
    assert resp.status == 400


async def test_getLanguages_with_bothExpectedParam_shouldPass(test_cli, generateData):
    params = {'page': 2, 'type': 'local'}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["total_results"] == 3
    assert len(resp_json["results"]) == 0
    assert resp_json["page"] == 2
    assert resp.status == 200


async def test_getLanguages_with_validPageNum_shouldPass(test_cli, generateData):
    params = {'page': 20}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["total_results"] == 5
    assert len(resp_json["results"]) == 0
    assert resp_json["page"] == 20
    assert resp.status == 200


async def test_getLanguages_with_invalidPageNum_shouldShowErrorMsg(test_cli, generateData):
    params = {'page': "test"}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Required Integer, found String"
    assert resp.status == 400


async def test_getLanguages_with_validTypeLanguage_shouldPass(test_cli, generateData):
    params = {'type': "foreign"}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["total_results"] == 2
    assert len(resp_json["results"]) == 2
    assert resp.status == 200
