from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

# Crear la sesión de Spark
spark = SparkSession.builder \
    .appName("Poblar tabla colores_mas_sancionados") \
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

# 2. Obtener los colores de los vehículos sancionados
vehiculos_sancionados_df = sanciones_informes_df.join(
    vehiculo_df,
    sanciones_informes_df["matricula"] == vehiculo_df["matricula"],
    "inner"
).select(vehiculo_df["color"])

# 3. Agrupar por color y contar el número de multas
colores_mas_sancionados_df = vehiculos_sancionados_df.groupBy(
    "color"
).agg(
    count("*").alias("num_multas")
)

# Mostrar los resultados intermedios
print("Colores de vehículos más sancionados:")
colores_mas_sancionados_df.show()

# Escribir el resultado en la tabla colores_mas_sancionados en Cassandra
colores_mas_sancionados_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="colores_mas_sancionados", keyspace="denuncias_dgt") \
    .mode("append") \
    .save()

print("Datos escritos en la tabla colores_mas_sancionados.")
