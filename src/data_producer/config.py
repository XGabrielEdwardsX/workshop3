import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC_RAW               = os.getenv('TOPIC_RAW', 'raw_data')
CSV_FILE                = os.getenv('CSV_FILE', './data/merge_happiness_ohe.csv')