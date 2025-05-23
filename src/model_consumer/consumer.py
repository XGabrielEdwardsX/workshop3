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
    model = load_model(MODEL_PATH)
    print(f"📦 Modelo cargado desde {MODEL_PATH}")

    consumer_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'model_consumer_group_v2',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
    }
    consumer = Consumer(consumer_conf)

    def on_assign_partitions(consumer_instance, partitions):
        for p in partitions:
            p.offset = OFFSET_BEGINNING
        consumer_instance.assign(partitions)
        print(f"✅ Partitions assigned, reading from beginning: {partitions}")

    consumer.subscribe([TOPIC_RAW], on_assign=on_assign_partitions)

    conn, cursor = connect_mysql(
        MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
    )

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                country VARCHAR(255),
                year INT,
                real_score FLOAT,
                predicted_score FLOAT,
                UNIQUE KEY idx_unique_prediction (country, year, real_score)
            ) ENGINE=InnoDB;
        """)
        conn.commit()
        print("✅ Tabla 'predictions' verificada/creada con clave única.")
    except Exception as e:
        print(f"❌ Error al crear/verificar la tabla 'predictions': {e}")
        consumer.close()
        if conn:
            conn.close()
        return

    print("🤖 Consumer de Kafka iniciado, leyendo mensajes…")
    processed_count = 0
    inserted_count = 0
    skipped_duplicates_count = 0

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"❌ Error de Kafka: {msg.error()}")
                    raise KafkaException(msg.error())

            try:
                record_data = json.loads(msg.value().decode('utf-8'))
            except json.JSONDecodeError as e:
                print(f"⚠️ Error al decodificar JSON del mensaje (offset {msg.offset()}): {e}. Mensaje: {msg.value()}")
                continue
            

            country = record_data.get('Country')
            real_score = record_data.get('Score')

            year_val = None 
            year_columns_to_check = ['Year_2019', 'Year_2018', 'Year_2017', 'Year_2016'] 
            
            for yr_col in year_columns_to_check:
                if record_data.get(yr_col) == 1 or str(record_data.get(yr_col)) == "1":
                    year_val = int(yr_col.split('_')[1])
                    break
            
            if year_val is None:
                year_val = 2015
                print(f"ℹ️ No se encontró columna Year_YYYY=1. Asumiendo año 2015 para offset {msg.offset()}.")
            country = record_data.get('Country')
            real_score = record_data.get('Score')

            if country is None or real_score is None:
                print(f"⚠️ Faltan 'Country' o 'Score' en el mensaje (offset {msg.offset()}). Saltando. Datos: {record_data}")
                continue

            try:
                features_for_model = extract_features(record_data)
            except Exception as e:
                print(f"⚠️ Error al extraer características para el mensaje (offset {msg.offset()}): {e}")
                print(f"   Datos del mensaje: {record_data}")
                continue

            predicted_score = model.predict([features_for_model])[0]

            try:
                cursor.execute(
                    "INSERT IGNORE INTO predictions (country, year, real_score, predicted_score) VALUES (%s, %s, %s, %s)",
                    (country, year_val, real_score, predicted_score)
                )
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"[{msg.offset():>5}] {str(country):<30} {year_val} → Real: {real_score:.3f}, Pred: {predicted_score:.3f} ✔️ Insertado")
                    inserted_count += 1
                else:
                    print(f"[{msg.offset():>5}] {str(country):<30} {year_val} → Real: {real_score:.3f}, Pred: {predicted_score:.3f} ⚠️ Duplicado, ignorado.")
                    skipped_duplicates_count += 1
                
                processed_count +=1

            except Exception as db_err:
                print(f"❌ Error al insertar en la base de datos para offset {msg.offset()}: {db_err}")
                conn.rollback()


    except KeyboardInterrupt:
        print("\n🛑 Consumidor detenido manualmente.")
    except Exception as e:
        print(f"\n💥 Error inesperado en el bucle del consumidor: {e}")
    finally:
        print("\n🔌 Cerrando recursos...")
        consumer.close()
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print(f"\n📊 Resumen del procesamiento:")
        print(f"   Mensajes procesados (intentos de inserción): {processed_count}")
        print(f"   Nuevas predicciones insertadas: {inserted_count}")
        print(f"   Predicciones duplicadas omitidas: {skipped_duplicates_count}")
        print("👋 Consumer finalizado.")

if __name__ == '__main__':
    run()