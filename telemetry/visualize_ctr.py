import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime, timedelta
from os.path import join, dirname, abspath

from config_reader import load_config

"""
This script is meant to be scheduled to run at the end of every day.
It reads from the Mongo DB and computes the CTR for the last ten days.
The CTRs are then plotted and the line chart is saved in the "ctrs" folder.
"""

TELEMETRY_FOLDER = abspath(dirname(__file__))


def get_mongo_db(host, port, name):
    """Return Mongo DB production database"""
    client = MongoClient(host, port)
    db = client[name]
    return db


if __name__ == "__main__":
    config = load_config()  # Get DB config
    db = get_mongo_db(
        config["db"]["host"], config["db"]["port"], config["db"]["name"]
    )  # Get prod MongoDB

    # Get list of dates for the last 10 days
    base = datetime.today()
    dates = [base - timedelta(days=x) for x in range(10)]
    dates.reverse()

    ctrs = []

    for d in dates:
        date = str(d.date())
        result = db.ctr_global.find_one(
            {"date": date}
        )  # Get corresponding CTR if exists
        if result and "num_clicks" in result and "num_recommends" in result:
            ctrs.append(round(result["num_clicks"] / result["num_recommends"], 3))
        else:
            ctrs.append(0)
    date = str(dates[-1].date())

    fig, ax = plt.subplots()
    ax.plot(dates, ctrs)
    ax.xaxis_date()  # interpret the x-axis values as dates
    fig.autofmt_xdate()  # make space for and rotate the x-axis tick labels
    plt.title("CTR vs. Day")
    plt.xlabel("Day")
    plt.ylabel("CTR")
    plt.savefig(join(TELEMETRY_FOLDER, "ctrs", f"ctrs-{date}.png"))  # Save CTR
