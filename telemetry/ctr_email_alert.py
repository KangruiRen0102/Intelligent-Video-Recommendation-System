from email.mime.text import MIMEText
import datetime
from pymongo import MongoClient
import smtplib
import sys
import subprocess

from config_reader import load_config

"""
This script is meant to be run at the end of each day. 
It checks whether today's CTR has fallen below a predefined threshold.
If it has, an email alert is sent to the team to notify them, allowing them to act swiftly.
"""

MIN_CTR = -1 # Set as dummy for now #0.0011  # Need to decide what the threshold is


def get_mongo_db(host, port, name):
    """Return Mongo DB production database"""
    client = MongoClient(host, port)
    db = client[name]
    return db


def send_ctr_alert(date, ctr):
    """
    Sends an email to alert the team that today's CTR has dropped below the predefined threshold.
         Parameters:
            date (str): A str of today's date (e.g., 2020-11-30).
            ctr (float): Today's CTR as of now.
    """
    sender = "team1_rs@outlook.com"
    receivers = ["alexa.hernandez@mail.mcgill.ca"]
    msg = MIMEText(
        f"Hello Team1,\n\nToday's CTR has dropped below {str(MIN_CTR*100)}%. The CTR is {str(ctr*100)}%.\nPlease "
        f"investigate immediately."
    )

    msg["Subject"] = "Team1 Recommendation Service - CTR Alert"
    msg["From"] = sender
    msg["To"] = ";".join(receivers)

    try:
        smtpObj = smtplib.SMTP("smtp.office365.com", 587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login("team1_rs@outlook.com", "team1*rs")
        smtpObj.sendmail(sender, receivers, msg.as_string())
        print("Successfully sent email")
    except smtplib.SMTPException as e:
        print("Error: unable to send email")


def todays_ctr(db, date):
    query = {"date": date}
    result = db.ctr_global.find_one(query)  # Find the row corresponding to today's CTR
    return result


if __name__ == "__main__":
    config = load_config()
    db = get_mongo_db(
        config["db"]["host"], config["db"]["port"], config["db"]["name"]
    )  # Get prod MongoDB
    date = str(datetime.date.today())  # Get today's date
    result = todays_ctr(db, date)

    if "num_recommends" not in result:
        sys.exit()  # No recommendations made today so far
    if "num_clicks" not in result:  # No clicks yet today
        send_ctr_alert(date, 0)
        sys.exit()
    ctr = round(result["num_clicks"] / result["num_recommends"], 3)  # Compute CTR
    if ctr < MIN_CTR:
        process = subprocess.Popen(["/bin/bash", "/home/localuser/PRODTeam1_RS/deployments/rollback.sh"])
        subprocess.communicate() # Call rollback script
        send_ctr_alert(date, ctr)
