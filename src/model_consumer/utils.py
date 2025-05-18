import json
import pickle
import uuid
from confluent_kafka import OFFSET_BEGINNING, KafkaException, KafkaError, Consumer
import mysql.connector

def load_model(path: str):
    print(f"📦 Loading model from {path}...")
    with open(path, 'rb') as f:
        model = pickle.load(f)
    print("✅ Model loaded.")
    return model

def make_consumer(bootstrap_servers: str, group_id: str, topic: str) -> Consumer:
    def on_assign(consumer, partitions):
        for p in partitions:
            p.offset = OFFSET_BEGINNING
        consumer.assign(partitions)
        print(f"✅ Partitions assigned at beginning: {partitions}")

    consumer = Consumer({
        'bootstrap.servers':  bootstrap_servers,
        'group.id':           group_id,
        'auto.offset.reset':  'earliest',
        'enable.auto.commit': False,
    })
    consumer.subscribe([topic], on_assign=on_assign)
    return consumer

def connect_mysql(host, port, user, password, database):
    conn = mysql.connector.connect(
        host=host, port=port, user=user,
        password=password, database=database
    )
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        country VARCHAR(100),
        year INT,
        real_score FLOAT,
        predicted_score FLOAT
    ) ENGINE=InnoDB;
    """)
    conn.commit()
    return conn, cur

def extract_features(rec: dict) -> list:
    feats = [
        rec.get(f, 0) for f in (
            ['Economy','Support','Health','Freedom','Trust','Generosity']
          + [
              'Region_Central and Eastern Europe',
              'Region_Eastern Asia',
              'Region_Latin America and Caribbean',
              'Region_Middle East and Northern Africa',
              'Region_North America',
              'Region_Southeastern Asia',
              'Region_Southern Asia',
              'Region_Sub-Saharan Africa',
              'Region_Western Europe'
            ]
          + ['Year_2016','Year_2017','Year_2018','Year_2019']
        )
    ]
    return feats
