from pymongo import MongoClient

"""
Script to extract user data from the Mongo DB user collection.
Use the 'get_users()' method to obtain a list of dicts corresponding to the docs in the user collection. 
"""

HOST = "fall2020-comp598-1.cs.mcgill.ca"
PORT = 27017
DB = "prod_db"


def get_users():
    """
    Returns a list containing all docs in users collection of the mongo db.
    """
    client = MongoClient(HOST, PORT)
    db = _mongo_db(client, DB)
    if "users" not in db.list_collection_names():
        raise ValueError(f"No user collection in {db.name}")
    users = [u for u in db.users.find()]
    return [_decode_movie_titles(u) for u in users]


def _mongo_db(client: MongoClient, db_name: str):
    """
    Returns the db called db_name from the provided MongoClient if it exists.
    Otherwise, throws a ValueError.
    Parameters
    ----------
    client : pymongo.MongoClient
        A client for MongoDB
    db_name : str
        The name of the mongo db
    """
    if db_name not in client.list_database_names():
        raise ValueError(f"No database called {db_name}")
    return client[db_name]


def _decode_movie_titles(user):
    keys_to_change = []
    for key in user.keys():
        if not key.startswith("_id") and key != "user_id":
            keys_to_change.append({"old": key, "new": _decode_movie_title(key)})

    for key in keys_to_change:
        user[key["new"]] = user.pop(key["old"])

    return user


def _decode_movie_title(title):
    return title.replace("\\u002e", ".").replace("\\u0024", "\$").replace("\\\\", "\\")


if __name__ == "__main__":
    users = get_users()
