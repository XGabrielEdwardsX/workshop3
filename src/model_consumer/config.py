# src/model_consumer/config.py
import os

# Kafka
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC_RAW               = os.getenv('TOPIC_RAW', 'raw_data')

# Modelo
MODEL_PATH              = os.getenv('MODEL_PATH', './model/catboost_model.pkl')

# MySQL
MYSQL_HOST     = os.getenv('MYSQL_HOST', 'mysql')
MYSQL_PORT     = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER     = os.getenv('MYSQL_USER', 'edwards')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'happiness')
