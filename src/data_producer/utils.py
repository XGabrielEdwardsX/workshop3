import json
import pandas as pd
from confluent_kafka import Producer

def make_producer(bootstrap_servers: str) -> Producer:
    return Producer({'bootstrap.servers': bootstrap_servers})

def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def serialize(record: dict) -> bytes:
    return json.dumps(record).encode('utf-8')

def delivery_report(err, msg):
    if err:
        key = msg.key().decode('utf-8') if msg.key() else None
        print(f"❌ Delivery failed for key={key}: {err}")
