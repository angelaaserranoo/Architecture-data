from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg

# Crear la sesión de Spark
spark = SparkSession.builder \
    .appName("Poblar tabla marcas_y_modelos_conductores_menos_respeto") \
    .config("spark.cassandra.connection.host", "127.0.0.1") \
    .getOrCreate()

# Leer las tablas originales desde Cassandra
sancion_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="sancion", keyspace="denuncias_dgt") \
    .load()

informe_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="informedenuncia", keyspace="denuncias_dgt") \
    .load()

vehiculo_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="vehiculo", keyspace="denuncias_dgt") \
    .load()

# Confirmar que los dataframes se han cargado correctamente
print("Datos de Sancion:")
sancion_df.show()
print("Datos de InformeDenuncia:")
informe_df.show()
print("Datos de Vehiculo:")
vehiculo_df.show()

# 1. Filtrar los informes de denuncia donde velocidad > limite
exceso_velocidad_df = informe_df.filter(col("velocidad") > col("limite_tramo")).select(
    "matricula", 
    (col("velocidad") - col("limite_tramo")).alias("exceso")
)

# 2. Unir con la tabla Vehiculo para obtener las marcas y modelos
vehiculos_exceso_df = exceso_velocidad_df.join(
    vehiculo_df,
    exceso_velocidad_df["matricula"] == vehiculo_df["matricula"],
    "inner"
).select(
    vehiculo_df["marca"],
    vehiculo_df["modelo"],
    "exceso"
)

# 3. Agrupar por marca y modelo, y calcular el promedio del exceso de velocidad
promedio_exceso_df = vehiculos_exceso_df.groupBy(
    "marca", "modelo"
).agg(
    avg("exceso").alias("promedio_exceso")
)

# Mostrar los resultados intermedios
print("Promedio de exceso de velocidad por marca y modelo:")
promedio_exceso_df.show()

# 4. Escribir en la tabla marcas_y_modelos_conductores_menos_respeto en Cassandra
promedio_exceso_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="marcas_y_modelos_conductores_menos_respeto", keyspace="denuncias_dgt") \
    .mode("append") \
    .save()

print("Datos escritos en la tabla marcas_y_modelos_conductores_menos_respeto.")
