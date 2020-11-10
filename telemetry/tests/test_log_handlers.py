from ..log_handlers import (
    recommendation_request,
    watch_request,
    rating_request,
    format_key,
)
from unittest.mock import MagicMock
import unittest


class TestConnection(unittest.TestCase):
    def test_recommendation_request(self):
        mock_db_collection = MagicMock()
        line = "2020-11-03T14:32:43.149,156483,recommendation request fall2020-comp598-1.cs.mcgill.ca:8082, status 200, result: existenz+1999, toy+story+2+1999, 65 ms"
        recommendation_request(line, mock_db_collection)
        mock_db_collection.update_many.assert_called_with(
            {"user_id": 156483},
            {
                "$inc": {
                    "existenz+1999.recommend_count": 1,
                    "toy+story+2+1999.recommend_count": 1,
                }
            },
            upsert=True,
        )

    def test_watch_request(self):
        mock_db_collection = MagicMock()
        line = "2020-11-03T14:32:43.149,156483, GET /data/m/walle+2008/20.mpg"
        watch_request(line, mock_db_collection)
        mock_db_collection.update_one.assert_called_with(
            {"user_id": 156483},
            {
                "$max": {
                    "walle+2008.watched": 20,
                }
            },
            upsert=True,
        )

    def test_rating_request(self):
        mock_db_collection = MagicMock()
        line = "2020-11-03T14:32:43.149,156483, GET /rate/walle+2008=4"
        rating_request(line, mock_db_collection)
        mock_db_collection.update_one.assert_called_with(
            {"user_id": 156483},
            {
                "$set": {
                    "walle+2008.rating": 4,
                }
            },
            upsert=True,
        )

    def test_format_key(self):
        movie_id = "  walle+2008 "
        attribute = "recommend_count"
        res = format_key(movie_id, attribute)
        self.assertEqual(res, "walle+2008.recommend_count")