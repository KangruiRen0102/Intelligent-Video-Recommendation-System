import re

from kafka import KafkaConsumer
import pandas as pd

""" A script to scrape the rate movie and watch movie events from the Kafka topic

    Check that you are connected to the McGill VPN before running.
"""


def get_consumer():
    """Return KafkaConsumer to consume records from movielog1 topic."""
    return KafkaConsumer(
        'movielog1',
        bootstrap_servers=["fall2020-comp598.cs.mcgill.ca:9092"],
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=lambda x: x.decode('utf-8'))


def get_rate_and_watch_movie_events(k_consumer: KafkaConsumer):
    """Return 2 pandas Dataframe: 1 containing all rate events, the other all watch events."""
    df_rate = pd.DataFrame(columns=["date", "user_id", "movie_id", "rating"])
    df_watch = pd.DataFrame(columns=["date", "user_id", "movie_id", "minute"])
    for record in k_consumer:
        value = record.value
        if "GET /rate/" in value:
            value = format_rate_event(value)
            print("RATE EVENT:", value)
            df_rate.loc[len(df_rate)] = value.split(",")
        if "GET /data/m" in value:
            value = format_watch_event(value)
            print("WATCH EVENT:", value)
            df_watch.loc[len(df_watch)] = value.split(",")
    return df_rate, df_watch


def format_rate_event(value: str):
    """Return formatted rate event as a csv str"""
    value = value.replace("=", ",")
    return value.replace("GET /rate/", "")


def format_watch_event(value: str):
    """Return formatted watch event as csv str."""
    idx = re.search("/[0-9]{1,}.mpg", value).start()  # Find idx of last "/" (right before minute)
    value = value[:idx] + "," + value[idx + 1:]  # Replace last "/" with comma
    value = value.replace("GET /data/m/", "")
    return value.replace(".mpg", "")


if __name__ == '__main__':
    # Get rate and watch events from Kafka topic
    consumer = get_consumer()
    df_rate, df_watch = get_rate_and_watch_movie_events(consumer)

    # Save rate and watch events to CSV files
    df_rate.to_csv("rate_events.csv", index=False)
    df_watch.to_csv("watch_events.csv", index=False)

    # Print number of rate and watch events
    print("Number of rate events", df_rate.shape[0])
    print("Number of watch events", df_watch.shape[0])
