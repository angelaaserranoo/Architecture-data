from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when

# Crear la sesión de Spark
spark = SparkSession.builder \
    .appName("Poblar tabla infracciones_titularidad") \
    .config("spark.cassandra.connection.host", "127.0.0.1") \
    .getOrCreate()

# Leer las tablas originales desde Cassandra
vehiculo_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="vehiculo", keyspace="denuncias_dgt") \
    .load()

sancion_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="sancion", keyspace="denuncias_dgt") \
    .load()

informe_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="informedenuncia", keyspace="denuncias_dgt") \
    .load()

# Confirmar que los dataframes se han cargado correctamente
print("Datos de Vehiculo:")
vehiculo_df.show()
print("Datos de Sancion:")
sancion_df.show()
print("Datos de InformeDenuncia:")
informe_df.show()

# 1. Crear atributo es_titular: sí/no
informe_con_titularidad_df = informe_df.join(
    vehiculo_df,
    informe_df["matricula"] == vehiculo_df["matricula"],
    "inner"
).withColumn(
    "es_titular",
    when(col("conductor") == col("titular"), True).otherwise(False)
)

# Confirmar datos con atributo es_titular
print("Datos con atributo es_titular:")
informe_con_titularidad_df.show()

# 2. Crear atributo es_sancionado: sí/no
informe_con_sancion_df = informe_con_titularidad_df.join(
    sancion_df.select("id").distinct().alias("sancion"),
    informe_con_titularidad_df["id"] == col("sancion.id"),
    "left_outer"
).withColumn(
    "es_sancionado",
    when(col("sancion.id").isNotNull(), True).otherwise(False)
).drop("sancion.id")

# Confirmar datos con atributo es_sancionado
print("Datos con atributo es_sancionado:")
informe_con_sancion_df.show()

# 3. Agrupar por es_titular y es_sancionado para calcular los conteos
conteos_df = informe_con_sancion_df.groupBy(
    "es_titular", "es_sancionado"
).agg(
    count("*").alias("conteo")
)

# Confirmar los conteos agrupados
print("Conteos agrupados por es_titular y es_sancionado:")
conteos_df.show()

# 4. Escribir los resultados en la tabla infracciones_titularidad en Cassandra
conteos_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="infracciones_titularidad", keyspace="denuncias_dgt") \
    .mode("append") \
    .save()

print("Datos escritos en la tabla infracciones_titularidad.")
