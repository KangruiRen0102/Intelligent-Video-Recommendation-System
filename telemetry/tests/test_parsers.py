import os
from random import randint
import sys
import unittest

from ..parsers import (
    parse_recommendation_request,
    parse_watch_request,
    parse_rating_request,
    time_to_date,
)


class TestParsers(unittest.TestCase):
    def test_parse_recommendation_request(self):
        true_uid = str(randint(1, 100000))
        line = "2020-11-03T14:32:43.149,{},recommendation request fall2020-comp598-1.cs.mcgill.ca:8082, status 200, result: duplicity+2009, toy+story+2+1999, the+judge+2014, 65 ms".format(
            true_uid
        )
        time, uid, recommendations = parse_recommendation_request(line)
        assert time == "2020-11-03T14:32:43.149"
        assert uid == true_uid
        assert recommendations == [
            "duplicity+2009",
            "toy+story+2+1999",
            "the+judge+2014",
        ]

    def test_parse_watch_request(self):
        true_uid = str(randint(1, 100000))
        true_min = str(randint(0, 160))
        line = "2020-08-05T10:37:43.149,{}, GET /data/m/lady+bird+2017/{}.mpg".format(
            true_uid, true_min
        )
        time, uid, mid, min = parse_watch_request(line)
        assert time == "2020-08-05T10:37:43.149"
        assert uid == true_uid
        assert mid == "lady+bird+2017"
        assert min == true_min

    def test_parse_rating_request(self):
        true_uid = str(randint(1, 100000))
        true_rating = str(randint(1, 5))
        line = "2020-11-03T14:32:43.149,{}, GET /rate/walle+2008={}".format(
            true_uid, true_rating
        )
        time, uid, mid, rating = parse_rating_request(line)
        assert time == "2020-11-03T14:32:43.149"
        assert uid == true_uid
        assert mid == "walle+2008"
        assert rating == true_rating

    def test_time_to_date(self):
        date = time_to_date("2020-08-20T15:22:43.149")
        assert date == "2020-08-20"
