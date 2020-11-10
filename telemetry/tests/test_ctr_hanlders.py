from datetime import datetime
import unittest
from unittest.mock import MagicMock

from ..ctr_handlers import recommend_event, watch_event


class TestConnection(unittest.TestCase):
    def test_recommend_event(self):
        mock_db_collection = MagicMock()
        line = "2020-11-03T14:32:43.149,159343,recommendation request fall2020-comp598-1.cs.mcgill.ca:8082, status 200, result: duplicity+2009, toy+story+2+1999, the+judge+2014, 65 ms"
        recommend_event(line, mock_db_collection)
        mock_db_collection.insert_one.assert_called_with(
            {
                "time": datetime.strptime(
                    "2020-11-03T14:32:43.149", "%Y-%m-%dT%H:%M:%S.%f"
                ),
                "user_id": 159343,
                "recommendations": [
                    "duplicity+2009",
                    "toy+story+2+1999",
                    "the+judge+2014",
                ],
            }
        )

    def test_watch_event(self):
        mock_db_collection = MagicMock()
        line = "2020-11-05T10:37:43.149,123045, GET /data/m/walle+2008/0.mpg"
        watch_event(line, mock_db_collection)
        mock_db_collection.insert_one.assert_called_with(
            {
                "time": datetime.strptime(
                    "2020-11-05T10:37:43.149", "%Y-%m-%dT%H:%M:%S.%f"
                ),
                "user_id": 123045,
                "movie_id": "walle+2008",
            }
        )
