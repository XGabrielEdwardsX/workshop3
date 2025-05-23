from .config import KAFKA_BOOTSTRAP_SERVERS, TOPIC_RAW, CSV_FILE
from .utils import make_producer, read_csv, serialize, delivery_report

def produce_csv():
    df = read_csv(CSV_FILE)
    print(f"▶️ Producing {CSV_FILE} with {len(df)} records...")
    producer = make_producer(KAFKA_BOOTSTRAP_SERVERS)
    for _, row in df.iterrows():
        record = row.to_dict()
        producer.produce(
            TOPIC_RAW,
            key=str(record.get('Country', '')).encode('utf-8'),
            value=serialize(record),
            callback=delivery_report
        )
        producer.poll(0)
    producer.flush()
    print("✅ Finished producing all records")

if __name__ == '__main__':
    produce_csv()
