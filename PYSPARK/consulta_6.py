from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

# Crear la sesión de Spark
spark = SparkSession.builder \
    .appName("Poblar tabla conductores_mas_infractores") \
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

persona_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="persona", keyspace="denuncias_dgt") \
    .load()

# Confirmar que los dataframes se han cargado correctamente
print("Datos de Sancion:")
sancion_df.show()
print("Datos de InformeDenuncia:")
informe_df.show()
print("Datos de Persona:")
persona_df.show()

# 1. Relacionar sanciones con informes para obtener los conductores
sanciones_informes_df = sancion_df.join(
    informe_df,
    sancion_df["id"] == informe_df["id"],
    "inner"
).select(informe_df["conductor"])

# 2. Contar las infracciones por conductor
infracciones_por_conductor_df = sanciones_informes_df.groupBy(
    "conductor"
).agg(
    count("*").alias("num_infracciones")
)

# Confirmar el conteo de infracciones por conductor
print("Conteo de infracciones por conductor:")
infracciones_por_conductor_df.show()

# 3. Unir con la tabla Persona para obtener los detalles de los conductores
conductores_infractores_df = infracciones_por_conductor_df.join(
    persona_df,
    infracciones_por_conductor_df["conductor"] == persona_df["dni"],
    "inner"
).select(
    persona_df["dni"].alias("dni_conductor"),
    persona_df["nombre"],
    persona_df["apellido_1"],
    persona_df["apellido_2"],
    persona_df["fecha_nacimiento"],
    persona_df["direccion"],
    persona_df["localidad"],
    persona_df["telefono"],
    persona_df["email"],
    "num_infracciones"
)

# Confirmar el resultado final
print("Conductores más infractores:")
conductores_infractores_df.show()

# 4. Escribir los resultados en la tabla conductores_mas_infractores en Cassandra
conductores_infractores_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="conductores_mas_infractores", keyspace="denuncias_dgt") \
    .mode("append") \
    .save()

print("Datos escritos en la tabla conductores_mas_infractores.")
