import pytest
import json
from app import create_app
import sys
sys.path.append("..")


@pytest.yield_fixture
def app():
    app = create_app("testing")
    yield app


@pytest.fixture
def test_cli(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))


async def test_index(test_cli):
    resp = await test_cli.get('/')
    assert resp.status == 200


async def test_getLanguages_with_no_query_param(test_cli):
    resp = await test_cli.get('/languages')
    resp_json = await resp.json()
    assert resp_json["total_results"] == 0
    assert resp_json["page"] == 1
    assert resp.status == 200


async def test_getLanguages_with_more_query_param(test_cli):
    params = {'page': 2, 'type': 'local', 'limit': 50}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Expecting less than 3 arguments"
    assert resp.status == 400


async def test_getLanguages_with_valid_query_param(test_cli):
    params = {'page': 2, 'type': 'local'}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["total_results"] == 0
    assert resp_json["page"] == 2
    assert resp.status == 200


async def test_getLanguages_with_query_param_page(test_cli):
    params = {'page': 20}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["total_results"] == 0
    assert resp_json["page"] == 20
    assert resp.status == 200


async def test_getLanguages_with_query_param_page_invalid(test_cli):
    params = {'page': "test"}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["message"] == "Required Integer, found String"
    assert resp.status == 400


async def test_getLanguages_with_query_param_type(test_cli):
    params = {'type': "foreign"}
    resp = await test_cli.get('/languages', data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["total_results"] == 0
    assert resp.status == 200


async def test_getLanguages_with_query_param_type_invalid(test_cli):
    params = {'type': 45}
    resp = await test_cli.get('/languages',  data=json.dumps(params))
    resp_json = await resp.json()
    assert resp_json["total_results"] == 0
    assert resp.status == 200
