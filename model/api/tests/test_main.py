import os
from random import randint, uniform
import re
import sys
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from ..main import app

text_type = "text/plain; charset=utf-8"
client = TestClient(app)


class TestRecommend(unittest.TestCase):
    def test_recommend_invalid_str_uid(self):
        response = client.get("/recommend/ten")
        assert response.status_code == 422
        assert response.content == b"user_id must be an integer."
        assert response.headers["content-type"] == text_type

    def test_recommend_invalid_float_uid(self):
        response = client.get("/recommend/{}".format(uniform(0, 1000)))
        assert response.status_code == 422
        assert response.content == b"user_id must be an integer."
        assert response.headers["content-type"] == text_type

    @patch("app.main.infer", return_value=list(range(20)))
    def test_recommend_valid_uid(self, mock_infer):
        response = client.get("/recommend/{}".format(randint(0, 20000)))
        assert response.status_code == 200
        assert response.content == b"0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19"
        assert response.headers["content-type"] == text_type


if __name__ == "__main__":
    unittest.main()
