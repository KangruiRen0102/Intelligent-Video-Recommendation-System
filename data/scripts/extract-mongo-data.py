from pymongo import MongoClient
from pymongo.database import Database

HOST = "fall2020-comp598-1.cs.mcgill.ca"
PORT = 27017
DB = "prod_db"


def mongo_db(client: MongoClient, db_name: str):
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
        raise ValueError("No database called {}".format(db_name))
    return client[db_name]


def get_users(db: Database):
    """
    Returns a list containing all docs in users collection of the provided mongo db.

    Parameters
    ----------
    db : pymongo.databases.Database
        A mongo database that contains a user collection
    """
    if "users" not in db.list_collection_names():
        raise ValueError("No user collection in {}".format(db.name))
    users = db.users
    return [u for u in users.find()]


if __name__ == "__main__":
    client = MongoClient(HOST, PORT)
    db = mongo_db(client, DB)
    users = get_users(db)
    client.close()
    print(users)
