import json
import time
import threading

from pymongo import MongoClient

import parsers as p


def timeout_set_remove(set, item, timeout):
    time.sleep(timeout)
    try:
        set.remove(item)
    except KeyError:
        pass


class TimedRecommendationSet(set):
    """
    Set that contains recommend events for prespecified time interval.
    """

    def add(self, recommend_event, timeout):
        """
        Add recommend event to the set.
        The recommend event will be removed from the set after timeout is complete.
        """
        if recommend_event not in self:
            set.add(self, recommend_event)
            t = threading.Thread(
                target=timeout_set_remove, args=(self, recommend_event, timeout)
            )
            t.start()


def recommendation_request(line, tr_set, collection, timeout=300):
    """
    Increments the recommend event count of the request date in the MongoDB collection.
    Adds the recommend event to the TimedRecommendationSet tr_set.

        Parameters:
            line (str): A line from the Kafka logs that corresponds to a recommend request
            tr_set (TimedRecommendationSet): The TimedRecommendationSet containing all recommend events from the last 5 mins
            collection (pymongo.Collection): Represents a collection within a database in MongoDB
            timeout (int): The amount of time, in seconds, to keep the recommend event on the TimedRecommendationSet.
    """
    # Parse the recommend event from the line
    time, user_id, recommendations, latency = p.parse_recommendation_request(line)
    date = p.time_to_date(time)

    # Add the recommend event to the TimedRecommendationSet set
    tr_set.add(
        json.dumps({"user_id": int(user_id), "recommendations": recommendations}),
        timeout,
    )

    # Update/insert the telemetry for the data
    collection.update_one(
        {"date": date},
        {
            "$inc": {
                "num_recommends": 1  # Increment the num_recommends by 1
            }
        },
        upsert=True,
    )


def watch_request(line, tr_set, collection):
    """
    Determines if the watch event corresponds to a click event.
    A click event occurs if the user watches a movie that is has been recommended within a predefined time interval (e.g. 5 mins).
    If a click event occurred, the click count of the request date is incremented in the MongoDB collection.

        Parameters:
            line (str): A line from the Kafka logs that corresponds to a watch request
            tr_set (TimedRecommendationSet): The TimedRecommendationSet containing all recommend events from the last 5 mins
            collection (pymongo.Collection): Represents a collection within a database in MongoDB
    """
    time, user_id, movie_id, _ = p.parse_watch_request(
        line
    )  # Parse the watch event from the line
    date = p.time_to_date(time)

    # Determine if a click event occurred
    clicked = False
    for item in tr_set:
        event = json.loads(item)
        if int(user_id) == event["user_id"] and movie_id in event["recommendations"]:
            clicked = True
            event_to_remove = item
            break
    if clicked:
        tr_set.remove(
            event_to_remove
        )  # Remove the corresponding recommend request from tr_set to avoid double counting
        collection.update_one(  # increment the click count
            {"date": date},
            {"$inc": {"num_clicks": 1}},
            upsert=True,
        )


"""Example
if __name__ == "__main__":
    client = MongoClient("fall2020-comp598-1.cs.mcgill.ca", 27017)
    db = client["prod_db"]
    s = TimedRecommendationSet()
    line = "2020-01-23T21:32:43.149,156483,recommendation request fall2020-comp598-1.cs.mcgill.ca:8082, status 200, result: existenz+1999, toy+story+2+1999, 30 ms"
    if "recommendation request" in line:
        recommendation_request(line, s, db.telemetry)
    elif "/data/" in line:
        watch_request(line, s, db.telemetry)
"""
