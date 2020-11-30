from functools import partial
from itertools import repeat

import parsers as p


def recommendation_request(line, collection):
    """
    Updates the number of times a movie was recommended to a user
    for all the movies in the recommendation.
    Parameters
    ----------
    line : str
        A line from the Kafka logs
    collection : pymongo.Collection
        Represents a collection within a database in MongoDB
    """
    time, user_id, recommendations, _ = p.parse_recommendation_request(line)

    if "status 200" in line:
        fcn = partial(_format_key, attribute="recommend_count")
        recommended = map(fcn, recommendations)
        collection.update_many(
            {"user_id": int(user_id)},
            {"$inc": dict(zip(recommended, repeat(1)))},
            upsert=True,
        )


def watch_request(line, collection):
    """
    Updates the maximum time to which a user has watched a movie
    Parameters
    ----------
    line : str
        A line from the Kafka logs
    collection : pymongo.Collection
        Represents a collection within a database in MongoDB
    """
    time, user_id, movie_id, minutes = p.parse_watch_request(line)

    if int(minutes) >= 0:
        collection.update_one(
            {"user_id": int(user_id)},
            {"$max": {_format_key(movie_id, "watched"): int(minutes.strip())}},
            upsert=True,
        )


def rating_request(line, collection):
    """
    Update the most recent rating given by a user for a given movie
    Parameters
    ----------
    line : str
        A line from the Kafka logs
    collection : pymongo.Collection
        Represents a collection within a database in MongoDB
    """
    time, user_id, movie_id, rating = p.parse_rating_request(line)

    if 1 <= int(rating) <= 5:
        collection.update_one(
            {"user_id": int(user_id)},
            {"$set": {_format_key(movie_id, "rating"): int(rating.strip())}},
            upsert=True,
        )


def _format_key(movie_id, attribute):
    """Return format movie title key."""
    encoded_title = _encode_movie_title(movie_id.strip())
    return f"{encoded_title}.{attribute}"


def _encode_movie_title(title):
    """Return the encoded movie title so that there are no illegal characters for MongoDB keys."""
    return title.replace("\\", "\\\\").replace("\$", "\\u0024").replace(".", "\\u002e")


""" Example
if __name__ == "__main__":

    HOST = "localhost"
    PORT = 27017
    client = MongoClient(HOST, PORT)
    db = client["ProdDB"]
    line = "2020-11-03T14:32:43.149,156483,recommendation request fall2020-comp598-1.cs.mcgill.ca:8082, status 200, result: existenz+1999, toy+story+2+1999, 65 ms"
    if "recommendation request" in line:
        recommendation_request(line, db.users)
    elif "/data/" in line:
        watch_request(line, db.users)
    elif "/rate/" in line:
        rating_request(line, db.users)
    else:
        print("Error: unhandled line", line)
"""
