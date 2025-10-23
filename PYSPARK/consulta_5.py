from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, avg, max

# Crear la sesión de Spark
spark = SparkSession.builder \
    .appName("Poblar tabla tramo_sentido_mas_conflictivo") \
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
    when(col("id").isNotNull(), col("velocidad"))  # Si hay sanción, usar la velocidad reflejada
    .otherwise(col("limite_tramo"))  # Si no hay sanción, usar el límite
)

# Confirmar datos con velocidad real calculada
print("Datos con velocidad real ajustada:")
denuncias_df.show()

# 2. Calcular el índice de exceso de velocidad
denuncias_df = denuncias_df.withColumn(
    "indice_exceso",
    ((col("velocidad_real") - col("limite_tramo")) / col("limite_tramo") * 100).cast("double")
)

# Confirmar datos con índice de exceso de velocidad
print("Datos con índice de exceso de velocidad:")
denuncias_df.show()

# 3. Agrupar por carretera, tramo y sentido, y calcular el índice promedio de exceso
indice_exceso_por_tramo_df = denuncias_df.groupBy(
    "nombre_carretera", "tramo", "sentido"
).agg(
    avg("indice_exceso").alias("indice_exceso")
)

# Confirmar el índice promedio de exceso
print("Índice promedio de exceso de velocidad por tramo y sentido:")
indice_exceso_por_tramo_df.show()

# 4. Escribir los resultados en la tabla tramo_sentido_mas_conflictivo en Cassandra
indice_exceso_por_tramo_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="tramo_sentido_mas_conflictivo", keyspace="denuncias_dgt") \
    .mode("append") \
    .save()

print("Datos escritos en la tabla tramo_sentido_mas_conflictivo.")
