import json
import csv
import uuid  # Para generar un ID único

from conversiones import convert_to_int
from conversiones import convert_to_date

# Función para crear un CSV desde un archivo JSON con los atributos específicos
def create_informe_denuncia_csv(json_file, csv_file):
    with open(json_file, 'r', encoding='latin1') as f:
        # Leer todo el contenido del archivo
        data = json.load(f)

        # Inicializar una lista para almacenar los datos
        informes_data = []

        # Iterar sobre los objetos en el archivo JSON
        for entry in data:
            # Extraer los datos de "Record" y "vehicle"
            record = entry.get('Record', {})
            vehicle = entry.get('vehicle', {})
            radar = entry.get('radar', {})
            road = entry.get('road', {})

            # Crear un diccionario con los datos mapeados
            informe = {}

            # Crear un ID único
            informe['id'] = entry.get('_id', None)  # '_id' del objeto (obligatorio)

            informe['nombre_carretera'] = road.get('name', None)  # 'road/name' (obligatorio)
            informe['tramo'] = convert_to_int(radar.get('mileage', None))  # 'radar/mileage' (obligatorio)
            informe['limite_tramo'] = convert_to_int(radar.get('speed limit', None))  # 'radar/speed limit' (obligatorio)
            informe['sentido'] = radar.get('direction', None)  # 'radar/direction' (obligatorio)
            informe['limite'] = convert_to_int(radar.get('speed limit', None))  # 'radar/speed limit' (obligatorio)
            informe['velocidad'] = convert_to_int(record.get('speed', None))  # 'Record/speed' (obligatorio)
            informe['fecha'] = convert_to_date(record.get('date', None))  # 'Record/date' (obligatorio)
            informe['matricula'] = vehicle.get('number plate', None)  # 'vehicle/number plate' (obligatorio)
            driver = vehicle.get('Driver', {})
            informe['conductor'] = driver.get('DNI', None)   # 'vehicle/Driver/DNI' (obligatorio)

            # Verificar si los campos obligatorios (id, fecha, matricula) están presentes
            if informe['id'] is None or informe['fecha'] is None or informe['matricula'] is None or \
                informe['nombre_carretera'] is None or informe['tramo'] is None or \
                informe['limite_tramo'] is None or informe['sentido'] is None or \
                informe['limite'] is None or informe['velocidad'] is None or \
                informe['conductor'] is None:
                continue  # Si falta algún campo obligatorio, el informe no se agrega

            # Agregar los datos del informe a la lista
            informes_data.append(informe)

        # Crear el archivo CSV para almacenar los datos
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Definir los encabezados del CSV
            fieldnames = ['id', 'nombre_carretera', 'tramo', 'limite_tramo', 'sentido', 'limite', 'velocidad', 'fecha', 'matricula', 'conductor']
            
            # Crear el escritor CSV
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Escribir los encabezados en el CSV
            writer.writeheader()

            # Escribir los datos de los informes en el CSV
            for informe in informes_data:
                writer.writerow(informe)
                print(f"Registro agregado: {informe}")

    print(f"Archivo CSV generado correctamente: {csv_file}")

# Ruta del archivo JSON de entrada y del archivo CSV de salida
json_file = 'sample.json'  # Ajusta la ruta del archivo JSON de entrada
csv_file = 'informe_denuncia.csv'  # Nombre del archivo CSV de salida

# Ejecutar la función para crear el CSV
create_informe_denuncia_csv(json_file, csv_file)
