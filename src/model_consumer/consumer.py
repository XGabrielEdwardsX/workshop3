# src/model_consumer/consumer.py

import json
from confluent_kafka import Consumer, KafkaException, KafkaError, OFFSET_BEGINNING
from .config import (
    KAFKA_BOOTSTRAP_SERVERS,
    TOPIC_RAW,
    MODEL_PATH,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
)
from .utils import load_model, connect_mysql, extract_features

def run():
    # Carga el modelo CatBoost
    model = load_model(MODEL_PATH)
    print(f"📦 Modelo cargado desde {MODEL_PATH}")

    # Creamos el consumidor con group.id estático y auto-commit
    consumer = Consumer({
        'bootstrap.servers':  KAFKA_BOOTSTRAP_SERVERS,
        'group.id':           'model_consumer_group',  # <- grupo fijo
        'auto.offset.reset':  'earliest',
        'enable.auto.commit': True,                    # <- auto‐commit de offsets
    })

    # Asignamos particiones para comenzar siempre desde el principio solo la 1ª vez
    def on_assign(consumer, partitions):
        for p in partitions:
            p.offset = OFFSET_BEGINNING
        consumer.assign(partitions)
        print(f"✅ Partitions assigned at beginning: {partitions}")

    consumer.subscribe([TOPIC_RAW], on_assign=on_assign)

    # Conexión a MySQL
    conn, cursor = connect_mysql(
        MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
    )
    # Aseguramos que la tabla exista
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            country VARCHAR(100),
            year INT,
            real_score FLOAT,
            predicted_score FLOAT
        ) ENGINE=InnoDB;
    """)
    conn.commit()

    print("🤖 Consumer iniciado, leyendo mensajes…")
    count = 0
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise KafkaException(msg.error())

            rec = json.loads(msg.value().decode('utf-8'))
            country = rec.get('Country', 'N/A')
            year = next(
                (int(y) for y in ('2019','2018','2017','2016')
                 if rec.get(f'Year_{y}', 0) == 1),
                2015
            )

            feats = extract_features(rec)
            pred = model.predict([feats])[0]
            real = rec.get('Score', None)

            print(f"[{msg.offset():>3}] {country:<20} {year} → real:{real}  pred:{pred:.3f}")

            # Inserta en MySQL
            cursor.execute(
                "INSERT INTO predictions (country, year, real_score, predicted_score) VALUES (%s, %s, %s, %s)",
                (country, year, real, pred)
            )
            conn.commit()

            count += 1
            if count >= 782:
                break

    finally:
        consumer.close()
        cursor.close()
        conn.close()
        print(f"\n📊 Total procesados: {count}")

if __name__ == '__main__':
    run()
