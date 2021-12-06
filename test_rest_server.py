from fastapi.testclient import TestClient

from .rest_server import app

client = TestClient(app)


def test_get_sentiment_without_param():

    response = client.get("/text/sentiment/", headers={})
    assert response.status_code == 405


def test_get_batch_sentiment_without_body():

    response = client.post("/text/sentiment/", headers={})
    assert response.status_code == 405


def test_get_sentiment():

    txt_id = "Hi im happy today."
    response = client.get("/text/summary/"+ txt_id +"{", headers={})
    assert response.status_code == 200