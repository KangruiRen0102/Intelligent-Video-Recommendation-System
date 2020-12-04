from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from pymongo import MongoClient

import ctr_handlers as ctr
import log_handlers as log
from config_reader import load_config


"""
This script continously polls the Kafka stream for new messages. 
For each new message, it then calls the appropriate handlers (e.g., ctr_handlers or log_handlers). 
The log handlers store implicit feedback to improve the training data 
    (e.g., for each user, the movies they rate, watch, and are recommended).
The ctr handlers compute the daily CTr and the daily CTR per model.
"""


def get_mongo_db(host, port, name):
    """Return Mongo DB production database"""
    client = MongoClient(host, port)
    db = client[name]
    return db


def get_kafka_consumer(group_id, host, port, topic):
    """Return consumer for Kafka topic"""
    consumer = KafkaConsumer(group_id=group_id,
                             auto_offset_reset="earliest",
                             bootstrap_servers=[f"{host}:{port}"],
                             value_deserializer=lambda x: x.decode('utf-8'))
    partition = TopicPartition(topic, 0)
    consumer.assign([partition])
    return consumer, partition


if __name__ == "__main__":
    config = load_config()
    db = get_mongo_db(config["db"]["host"], config["db"]["port"], config["db"]["name"])   # Get prod mongo db
    consumer, partition = get_kafka_consumer(config["kafka"]["group_id"],  # Get Kafka consumer and partition
                                             config["kafka"]["host"],
                                             config["kafka"]["port"],
                                             config["kafka"]["topic"])

    while True:
        results = consumer.poll(timeout_ms=10000)  # Poll new Kafka records
        if results:
            msgs = list(results.values())[0]
            for msg in msgs:
                line = msg.value
                if "recommendation request" in line:
                    log.recommendation_request(line, db.users)
                elif "/data/" in line:
                    log.watch_request(line, db.users)
                    ctr.watch_request(line, db.movies, db.recommendations, db.ctr_per_model, db.ctr_global)
                elif "/rate/" in line:
                    log.rating_request(line, db.users)
                else:
                    print("Error: unhandled line", line)
        consumer.commit()
    consumer.close()
