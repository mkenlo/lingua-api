import pytest
import json
from .factory import (insertDummyLanguages, insertDummySentences, insertDummyTranslations,
                      insertDummyUsers, removeCollections, )
from app import create_app
from app.models import *
import sys
sys.path.append("..")


NUM_TOTAL_USERS = 10
FIRST_USERNAME = "hmyron"
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


async def test_getUsers_with_noParam_shouldPass(test_cli, preFillDB):
    resp = await test_cli.get('/users')
    resp_json = await resp.json()
    assert resp_json["total_results"] == NUM_TOTAL_USERS
    assert len(resp_json["results"]) == NUM_TOTAL_USERS
    assert resp_json["page"] == 1
    assert resp_json["results"][0]["username"] == FIRST_USERNAME
    assert resp.status == 200


async def test_addUsers_with_missingRequiredField_shouldFailed(test_cli):
    params = {
        "fullname":  "Snow",
        "location": "testVille"}
    resp = await test_cli.post('/users', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Missing required <username> field"
    assert resp.status == 400


async def test_addUsers_with_validParam_shouldPass(test_cli, preFillDB):
    num_before_insertion = Users.objects.count()
    params = {"username": "jsnow", "fullname":  "John Snow", "location": "testVille",
              "avatar": "https://lorem.org/ipsum.jpg"}
    resp = await test_cli.post('/users', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Added One Item"
    assert Users.objects.count() == num_before_insertion+1


async def test_getTranslationsbyUserID_with_knownID_shouldPass(test_cli, preFillDB):
    user = Users.objects.first()
    resp = await test_cli.get('/users/{}/translations'.format(user.pk))
    resp_json = await resp.json()
    assert resp.status == 200
    assert resp_json["page"] == 1
    assert resp_json["total_results"] == NUM_TRANSLATIONS_FROM_TESTSET
    assert resp_json["results"][0]["author"] == user.username
