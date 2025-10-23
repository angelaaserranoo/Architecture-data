from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

# Crear la sesión de Spark
spark = SparkSession.builder \
    .appName("Poblar tabla sanciones_por_marca_modelo") \
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

# Relacionar las tablas siguiendo la lógica definida
# 1. Relacionar sanciones con informes para obtener las matrículas
sanciones_informes_df = sancion_df.join(
    informe_df,
    sancion_df["id"] == informe_df["id"],
    "inner"
).select(informe_df["matricula"])

# 2. Obtener las marcas y modelos de los vehículos sancionados
vehiculos_sancionados_df = sanciones_informes_df.join(
    vehiculo_df,
    sanciones_informes_df["matricula"] == vehiculo_df["matricula"],
    "inner"
).select(vehiculo_df["marca"], vehiculo_df["modelo"])

# 3. Agrupar por marca y modelo y contar el número de multas
sanciones_por_marca_modelo_df = vehiculos_sancionados_df.groupBy(
    "marca", "modelo"
).agg(
    count("*").alias("num_multas")
)

# Mostrar los resultados intermedios
print("Sanciones por marca y modelo:")
sanciones_por_marca_modelo_df.show()

# Escribir el resultado en la tabla sanciones_por_marca_modelo en Cassandra
sanciones_por_marca_modelo_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="sanciones_por_marca_modelo", keyspace="denuncias_dgt") \
    .mode("append") \
    .save()

print("Datos escritos en la tabla sanciones_por_marca_modelo.")
