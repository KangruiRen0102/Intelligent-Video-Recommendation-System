from datetime import date
from pymongo import MongoClient
from threading import Event, Thread
from os.path import join, dirname, abspath

# Mongo DB configuration variables
DB_HOST = "fall2020-comp598-1.cs.mcgill.ca"
DB_PORT = 27017
DB = "prod_db"
ROOT = abspath(join(dirname(__file__), ".."))
MODEL_PATH = join(ROOT, "checkpoint", "model")


# Taken from https://gist.github.com/duckythescientist/d839603efb3dc7c828f9
class Periodic(object):
    """Periodically run a function with arguments asynchronously in the background
    Period is a float of seconds.
    Don't expect exact precision with timing.
    Threading is used instead of Multiprocessing because we need shared memory
    otherwise changes made by the function to arguments won't be reflected in
    the rest of the script.
    """

    def __init__(self, func, period, args=[]):
        args.append(_get_mongo_db())
        self.period = period
        self.func = func
        self.args = args  # Add MongoDB collection as arg
        self.seppuku = Event()

    def start(self):
        self.seppuku.clear()
        self.proc = Thread(target=self._doit)
        self.proc.start()

    def stop(self):
        """Nearly immediately kills the Periodic function"""
        self.seppuku.set()
        self.proc.join()

    def _doit(self):
        while True:
            self.seppuku.wait(self.period)
            if self.seppuku.is_set():
                break
            self.func(*self.args)


def store_recommendations(recommendations, model_version, db):
    """
    Stores recommendations in Mongo DB collection

        Parameters:
            recommendations (list): A list containing recommendations to store in the Mongo DB collection.
            model_version: The version of the model currently making recommendations.
            db (pymongo.Database): The production MongoDB.
    """
    if recommendations:
        # Insert the recommendations into the mongoDB
        db.recommendations.insert_many(recommendations)

        # Update the # of recommendations made by the model version today
        db.ctr_per_model.update_one(
            {"model_version": model_version, "date": str(date.today())},
            {"$inc": {"num_recommends": len(recommendations)}},
            upsert=True,
        )

        # Update the # of recommendations made today for the global CTR
        db.ctr_global.update_one(
            {"date": str(date.today())},
            {"$inc": {"num_recommends": len(recommendations)}},
            upsert=True,
        )

        recommendations.clear()  # Clear the recommendations so that they are not added twice


def get_model_version():
    """Returns the current model version that is being used."""
    d = {}
    file = MODEL_PATH + "/model_version.txt"
    with open(file) as f:
        for line in f:
            (key, value) = line.split(",")
            d[key] = value
    return d["model version"]


def _get_mongo_db():
    """Return Mongo DB."""
    client = MongoClient(DB_HOST, DB_PORT)
    db = client[DB]
    return db



