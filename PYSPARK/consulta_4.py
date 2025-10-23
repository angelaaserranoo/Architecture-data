from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, avg

# Crear la sesión de Spark
spark = SparkSession.builder \
    .appName("Poblar tabla exceso_velocidad_medio_por_carretera") \
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

# Confirmar que los dataframes se han cargado correctamente
print("Datos de Sancion:")
sancion_df.show()
print("Datos de InformeDenuncia:")
informe_df.show()

# 1. Identificar los registros que no obtuvieron sanción
denuncias_con_sancion_df = sancion_df.select("id").distinct()
denuncias_df = informe_df.join(
    denuncias_con_sancion_df,
    informe_df["id"] == denuncias_con_sancion_df["id"],
    "left_outer"
).withColumn(
    "velocidad_real",
    when(denuncias_con_sancion_df["id"].isNotNull(), col("velocidad"))  # Si hay sanción, usar la velocidad reflejada
    .otherwise(col("limite_tramo"))  # Si no hay sanción, usar el límite
)


# Confirmar datos con velocidad real calculada
print("Datos con velocidad real ajustada:")
denuncias_df.show()

# 2. Calcular el exceso de velocidad en porcentaje
denuncias_df = denuncias_df.withColumn(
    "exceso_velocidad_porcentaje",
    ((col("velocidad_real") - col("limite_tramo")) / col("limite_tramo") * 100).cast("double")
)

# Confirmar datos con exceso de velocidad calculado
print("Datos con exceso de velocidad en porcentaje:")
denuncias_df.show()

# 3. Agrupar por nombre_carretera y calcular el promedio del exceso de velocidad
exceso_velocidad_medio_df = denuncias_df.groupBy("nombre_carretera").agg(
    avg("exceso_velocidad_porcentaje").alias("exceso_velocidad_medio")
)

# Confirmar el promedio de exceso de velocidad
print("Promedio de exceso de velocidad por carretera:")
exceso_velocidad_medio_df.show()

# 4. Escribir los resultados en la tabla exceso_velocidad_medio_por_carretera en Cassandra
exceso_velocidad_medio_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="exceso_velocidad_medio_por_carretera", keyspace="denuncias_dgt") \
    .mode("append") \
    .save()

print("Datos escritos en la tabla exceso_velocidad_medio_por_carretera.")
