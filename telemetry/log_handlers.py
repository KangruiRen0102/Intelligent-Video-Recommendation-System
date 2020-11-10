import logging
from pymongo import MongoClient
from itertools import repeat
from functools import partial


def format_key(movie_id, attribute):
    return f"{movie_id.strip()}.{attribute}"


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
    time, user_id, _, _ = line[: line.find(", result:")].split(",")
    recommendations = line[line.rfind("result:") + 7 : line.rfind(", ")]

    if "status 200" in line:
        fcn = partial(format_key, attribute="recommend_count")
        recommended = map(fcn, recommendations.split(","))
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
    time, user_id, _ = line.split(",")
    movie_id, minutes = line[line.find("/m/") + 3 : line.rfind(".mpg")].split("/")

    if int(minutes) >= 0:
        collection.update_one(
            {"user_id": int(user_id)},
            {"$max": {format_key(movie_id, "watched"): int(minutes.strip())}},
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
    time, user_id, _ = line.split(",")
    rating_part = line[line.rfind("/") + 1 :]
    movie_id, rating = rating_part.split("=")

    if 1 <= int(rating) <= 5:
        collection.update_one(
            {"user_id": int(user_id)},
            {"$set": {format_key(movie_id, "rating"): int(rating.strip())}},
            upsert=True,
        )


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
