from pymongo import MongoClient
from threading import Event, Thread

# Mongo DB configuration variables
DB_HOST = "fall2020-comp598-1.cs.mcgill.ca"
DB_PORT = 27017
DB = "prod_db"


class Periodic(object):
    """Periodically run a function with arguments asynchronously in the background
    Period is a float of seconds.
    Don't expect exact precision with timing.
    Threading is used instead of Multiprocessing because we need shared memory
    otherwise changes made by the function to arguments won't be reflected in
    the rest of the script.
    """

    def __init__(self, func, period, args=[]):
        args.append(_get_mongo_coll())
        print("INITIALIZING")
        self.period = period
        self.func = func
        self.args = args  # Add MongoDB collection as arg
        print(self.args)
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


def store_recommendations(recommendations, model_version, mongo_coll):
    print(recommendations)
    print("VERSION", model_version)
    recommendations.clear()


def get_model_version():
    return 1


def _get_mongo_coll():
    """Return Mongo DB collection to store recommendations in."""
    client = MongoClient(DB_HOST, DB_PORT)
    db = client[DB]
    return db.recommendations