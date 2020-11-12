import json
from random import randint
import time
import unittest
from unittest.mock import MagicMock

from ..telemetry_handlers import (
    TimedRecommendationSet,
    recommendation_request,
    watch_request,
)


class TestTelemetryHandlers(unittest.TestCase):
    def setUp(self):
        self.tr_set = TimedRecommendationSet()
        self.mock_coll = MagicMock()
        self.uid = randint(0, 100000)

    def test_recommendation_request_success(self):
        real_latency = randint(1, 100)
        line = "2020-11-03T14:32:43.149,23,recommendation request fall2020-comp598-1.cs.mcgill.ca:8082, status 200, result: duplicity+2009, {} ms".format(
            real_latency
        )
        recommendation_request(line, self.tr_set, self.mock_coll, 1)
        self.mock_coll.update_one.assert_called_with(
            {"date": "2020-11-03"},
            {"$inc": {"num_recommends": 1, "total_latency": real_latency}},
            upsert=True,
        )
        assert len(self.tr_set) == 1
        assert (
            self.tr_set.pop()
            == '{"user_id": 23, "recommendations": ["duplicity+2009"]}'
        )

    def test_recommendation_request_failure(self):
        real_latency = randint(1, 100)
        line = "2020-10-23T14:32:43.149,23,recommendation request fall2020-comp598-1.cs.mcgill.ca:8082, status 0, result: Connection refused: fall2020-comp598-1.cs.mcgill.ca/132.206.51.156:8082, 1369 ms"
        recommendation_request(line, self.tr_set, self.mock_coll, 1)
        self.mock_coll.update_one.assert_called_with(
            {"date": "2020-10-23"},
            {"$inc": {"num_conn_refused": 1}},
            upsert=True,
        )
        assert len(self.tr_set) == 0

    def test_watch_request_recommended_movie(self):
        self.tr_set.add(
            json.dumps(
                {
                    "user_id": self.uid,
                    "recommendations": ["movie1+2019", "movie2+2013", "movie3+2000"],
                }
            ),
            3,
        )
        line = "2020-10-23T14:32:43.149,{}, GET /data/m/movie1+2019/20.mpg".format(
            self.uid
        )
        watch_request(line, self.tr_set, self.mock_coll)
        self.mock_coll.update_one.assert_called_with(
            {"date": "2020-10-23"},
            {"$inc": {"num_clicks": 1}},
            upsert=True,
        )
        assert len(self.tr_set) == 0

    def test_watch_request_unrecommended_movie(self):
        self.tr_set.add(
            json.dumps(
                {"user_id": self.uid, "recommendations": ["movie1+2019", "movie2+2013"]}
            ),
            3,
        )
        line = "2020-10-23T14:32:43.149,{}, GET /data/m/movie5+2009/20.mpg".format(
            self.uid
        )
        watch_request(line, self.tr_set, self.mock_coll)
        assert (
            not self.mock_coll.update_one.called
        )  # Make sure the collection was not updated
        assert len(self.tr_set) == 1  # Make sure the recommend event was not removed

    def test_watch_request_uid_with_no_recommendations(self):
        self.tr_set.add(
            json.dumps(
                {"user_id": self.uid, "recommendations": ["movie3+2012", "movie7+2011"]}
            ),
            3,
        )
        line = "2020-10-23T14:32:43.149,{}, GET /data/m/movie3+2012/20.mpg".format(
            self.uid + 1
        )
        watch_request(line, self.tr_set, self.mock_coll)
        assert (
            not self.mock_coll.update_one.called
        )  # Make sure the collection was not updated
        assert len(self.tr_set) == 1  # Make sure the recommend event was not removed

    def test_watch_request_recommend_event_timed_out(self):
        self.tr_set.add(
            json.dumps(
                {"user_id": self.uid, "recommendations": ["movie9+1995", "movie4+2001"]}
            ),
            0.1,
        )
        line = "2020-10-23T14:32:43.149,{}, GET /data/m/movie4+2001/20.mpg".format(
            self.uid
        )
        time.sleep(0.2)
        watch_request(line, self.tr_set, self.mock_coll)
        assert (
            not self.mock_coll.update_one.called
        )  # Make sure the collection was not updated
        assert len(self.tr_set) == 0  # tr_set is empty since recommend event timed out

