import os
from random import randint, uniform
import re
import sys
import unittest

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(".."))
from app.main import app

text_type = "text/plain; charset=utf-8"


class TestRecommend(unittest.TestCase):
    def test_recommend_invalid_str_uid(self):
        with TestClient(app) as client:
            response = client.get("/recommend/ten")
        assert response.status_code == 422
        assert response.content == b"user_id must be an integer."
        assert response.headers["content-type"] == text_type

    def test_recommend_invalid_float_uid(self):
        with TestClient(app) as client:
            response = client.get("/recommend/{}".format(uniform(0, 1000)))
        assert response.status_code == 422
        assert response.content == b"user_id must be an integer."
        assert response.headers["content-type"] == text_type

    def test_recommend_valid_uid(self):
        with TestClient(app) as client:
            response = client.get("/recommend/{}".format(randint(0, 20000)))
        assert response.status_code == 200
        assert re.match(r"([0-9]{1,},){19}[0-9]{1,}", response.text)
        assert response.headers["content-type"] == text_type


if __name__ == "__main__":
    unittest.main()
