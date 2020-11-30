from kafka import KafkaConsumer
from pymongo import MongoClient

import ctr_handlers as ctr
import log_handlers as log


# Mongo DB configuration variables
DB_HOST = "fall2020-comp598-1.cs.mcgill.ca"
DB_PORT = 27017
DB = "prod_db"

# Kafka topic configuration variables
TOPIC = "movielog1"
K_HOST = "fall2020-comp598.cs.mcgill.ca"
K_PORT = 9092
GROUP_ID = "telemetry-collector"


def get_mongo_db():
    """Return Mongo DB production database"""
    client = MongoClient(DB_HOST, DB_PORT)
    db = client[DB]
    return db


def get_kafka_consumer():
    """Return consumer for Kafka topic"""
    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=[f"{K_HOST}:{K_PORT}"],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=GROUP_ID,
        value_deserializer=lambda x: x.decode('utf-8'))


if __name__ == "__main__":
    db = get_mongo_db()
    kafka_consumer = get_kafka_consumer()
    TRS = ctr.TimedRecommendationSet()

    for record in kafka_consumer:
        line = record.value
        print("LINE:", line)
        if "recommendation request" in line:
            log.recommendation_request(line, db.users)
            ctr.recommendation_request(line, TRS, db.telemetry)
        elif "/data/" in line:
            log.watch_request(line, db.users)
            ctr.watch_request(line, TRS, db.telemetry)
        elif "/rate/" in line:
            log.rating_request(line, db.users)
        else:
            print("Error: unhandled line", line)

    kafka_consumer.close()
