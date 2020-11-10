from datetime import datetime
from pymongo import MongoClient


def recommend_event(line, collection):
    """
    Inserts a new document into the provided collection.
    The new document captures the recommend event in the provided line.
    Parameters
    ----------
    line : str
        A line from the Kafka logs
    collection : pymongo.Collection
        Represents a collection within a database in MongoDB
    """
    time, user_id, _, _ = line[: line.find(", result:")].split(",")
    recommendations = (
        line[line.rfind("result:") + 7 : line.rfind(", ")].replace(" ", "").split(",")
    )
    collection.insert_one(
        {
            "time": datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f"),
            "user_id": int(user_id),
            "recommendations": recommendations,
        }
    )


def watch_event(line, collection):
    """
    Inserts a new document into the provided collection.
    The new document captures the watch event in the provided line.
    Parameters
    ----------
    line : str
        A line from the Kafka logs
    collection : pymongo.Collection
        Represents a collection within a database in MongoDB
    """
    time, user_id, _ = line.split(",")
    movie_id, minutes = line[line.find("/m/") + 3 : line.rfind(".mpg")].split("/")
    collection.insert_one(
        {
            "time": datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f"),
            "user_id": int(user_id),
            "movie_id": movie_id,
        }
    )


"""Example
if __name__ == "__main__":
    HOST = "fall2020-comp598-1.cs.mcgill.ca"
    PORT = 27017
    client = MongoClient(HOST, PORT)
    db = client["ProdDB"]
    line = "2020-11-03T14:32:43.149,156483,recommendation request fall2020-comp598-1.cs.mcgill.ca:8082, status 200, result: existenz+1999, toy+story+2+1999, 65 ms"
    if "recommendation request" in line and "status 200" in line:
        recommend_event(line, db.recommend_events)
    elif "/data/" in line and "/0.mpg" in line:
        watch_event(line, db.watch_events)
    client.close()
"""
