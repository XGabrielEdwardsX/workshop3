# Proyecto de Análisis y Predicción de la Felicidad Mundial

Pipeline ETL y análisis predictivo para estudiar los factores que influyen en la felicidad mundial, utilizando datos de los reportes de felicidad de 2015 a 2019. Se emplearon herramientas como Python, Pandas, Scikit-learn, CatBoost, Kafka, MySQL y Docker para un flujo completo de procesamiento y modelado.

📂 **Estructura del Repositorio**  
```
├── data/  
│   ├── 2015.csv                    # Datos de felicidad 2015  
│   ├── 2016.csv                    # Datos de felicidad 2016  
│   ├── 2017.csv                    # Datos de felicidad 2017  
│   ├── 2018.csv                    # Datos de felicidad 2018  
│   ├── 2019.csv                    # Datos de felicidad 2019  
│   ├── merge_happiness.csv         # Datos consolidados y limpios  
│   ├── merge_happiness_ohe.csv     # Datos con One-Hot Encoding para modelado  
│   └── test_data/  
│       └── happiness_test_data.csv # Conjunto de prueba para Kafka  
├── docker-compose.yml              # Configuración de servicios Docker  
├── Dockerfile.consumer             # Imagen para el consumidor de Kafka  
├── Dockerfile.producer             # Imagen para el productor de Kafka  
├── model/  
│   └── catboost_model.pkl          # Modelo CatBoost entrenado  
├── mysql-init/  
│   └── init.sh                     # Inicialización de la base de datos MySQL  
├── notebooks/  
│   ├── 001_eda.ipynb               # Análisis exploratorio inicial  
│   ├── 002_transform_merge_eda.ipynb # Transformación y unificación de datos  
│   ├── train.ipynb                 # Entrenamiento y evaluación del modelo  
│   ├── R2_database_recalculated.ipynb # Evaluación de métricas desde la base de datos  
├── requirements-consumer.txt       # Dependencias para el consumidor  
├── requirements-producer.txt       # Dependencias para el productor  
├── requirements.txt                # Dependencias para desarrollo local  
├── src/  
│   ├── data_producer/             # Módulo del productor de Kafka  
│   │   ├── producer.py  
│   │   └── utils.py  
│   └── model_consumer/            # Módulo del consumidor y predicción  
│       ├── consumer.py  
│       └── utils.py  
└── wait-for-kafka.sh              # Script para esperar a Kafka  
```

🛠️ **Tecnologías Utilizadas**  
| Categoría             | Herramientas                              |  
|-----------------------|-------------------------------------------|  
| Lenguaje              | Python                                    |  
| Procesamiento de Datos | Pandas, NumPy                             |  
| Machine Learning      | Scikit-learn, CatBoost                    |  
| Visualización         | Matplotlib, Seaborn                       |  
| Mensajería/Streaming  | Apache Kafka (confluent-kafka)            |  
| Base de Datos         | MySQL                                     |  
| Orquestación          | Docker, Docker Compose                    |  
| Entorno de Desarrollo | Jupyter Notebooks, Entornos Virtuales     |  

🚀 **Guía de Configuración**  
1. **Clonar el Repositorio**  
   ```bash
   git clone https://github.com/XGabrielEdwardsX/workshop3
   cd workshop3
   ```

2. **Configuración de Variables de Entorno**  
   Cree un archivo `.env` en la raíz del proyecto con las siguientes variables (ajuste los valores según su configuración):  
   ```env
   MYSQL_ROOT_PASSWORD=
   MYSQL_DATABASE=happiness
   MYSQL_USER=
   MYSQL_PASSWORD=
   KAFKA_BOOTSTRAP_SERVERS=kafka:9092
   TOPIC_RAW=raw_data
   MODEL_PATH=./model/catboost_model.pkl
   MYSQL_HOST_NOTEBOOK=localhost
   MYSQL_PORT_NOTEBOOK=3308
   ```

3. **Ejecutar Servicios con Docker**  
   Inicia Zookeeper, Kafka, MySQL, el productor y el consumidor:  
   ```bash
   docker-compose up -d --build
   ```

4. **Ejecución Local de Notebooks**  
   Para explorar los notebooks localmente:  
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

5. **Verificar Resultados**  
   Conéctese a MySQL (puerto 3308) y consulte la tabla `predictions` en la base de datos `happiness`.

🔄 **Flujo del Pipeline**  
1. **Análisis Exploratorio (EDA)**  
   - Se analizaron los datos de 2015-2019 (782 registros únicos).  
   - Se eliminó `Dystopia Residual` por su dependencia con la variable objetivo (`Score`).  
   - Un valor nulo en `Perceptions of corruption` (2018) fue identificado y tratado.

2. **Transformación y Unificación**  
   - Se estandarizaron columnas: `Country`, `Year`, `Score`, `Economy`, `Support`, `Health`, `Freedom`, `Trust`, `Generosity`, `Region`.  
   - Se descartaron columnas irrelevantes como `Happiness Rank`.  
   - Se aplicó One-Hot Encoding a `Region` y `Year`, generando `merge_happiness_ohe.csv`.  
   - Análisis de correlación: `Economy` (0.79) y `Health` (0.74) son los factores más influyentes. Variaciones regionales muestran que `Freedom` y `Trust` son clave en regiones desarrolladas, mientras que `Economy` predomina en regiones en desarrollo.

3. **Entrenamiento del Modelo**  
   - Se probaron múltiples algoritmos; CatBoost obtuvo el mejor rendimiento (R² = 0.859).  
   - Características principales: `Economy` (25.6%), `Health` (15.4%), `Freedom` (12.4%).  
   - Modelo guardado en `catboost_model.pkl`.

4. **Pipeline con Kafka y MySQL**  
   - **Productor**: Lee `happiness_test_data.csv` y envía datos a Kafka (`raw_data`).  
   - **Consumidor**: Procesa mensajes, predice `Score` con CatBoost y almacena resultados en MySQL (`predictions`).  
   - Docker orquesta todos los servicios, con inicialización automática de MySQL.

5. **Evaluación de Métricas en la Base de Datos**  
   - El notebook `R2_database_recalculated.ipynb` calcula métricas utilizando los datos almacenados en la tabla `predictions` de MySQL.  
   - Resultados obtenidos:  
     ```
     --- Métricas de Evaluación del Modelo ---
     R²: 0.7795
     MAE: 0.4056
     MSE: 0.2682
     RMSE: 0.5179
     Varianza Explicada: 0.7810
     ```
   - El R² (0.7795) indica un rendimiento sólido, aunque inferior al obtenido en el entrenamiento (0.859), posiblemente debido a diferencias en los datos procesados por el pipeline.

🔑 **Conclusiones**  
- El modelo CatBoost predice la felicidad con alta precisión (R² ≈ 0.86 en entrenamiento, 0.78 en datos de la base).  
- Factores clave: economía, salud, libertad, apoyo social y confianza; la generosidad tiene menor impacto.  
- Las prioridades varían por región: libertad en Europa Occidental, confianza en Norteamérica, economía en regiones en desarrollo.  

📝 **Archivos Adicionales**  
- `requirements.txt`: Dependencias para desarrollo local.  
- `requirements-producer.txt` y `requirements-consumer.txt`: Dependencias para Docker.  
- `mysql-init/init.sh`: Inicialización de MySQL.  
- `wait-for-kafka.sh`: Asegura la disponibilidad de Kafka.  
- `.env`: Configuración de variables de entorno para MySQL y Kafka.
