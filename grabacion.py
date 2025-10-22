import json
import csv
import uuid  # Para generar un ID único

from conversiones import convert_to_int

# Función para crear un CSV desde un archivo JSON con los atributos específicos para "Grabacion"
def create_grabacion_csv(json_file, csv_file):
    with open(json_file, 'r', encoding='latin1') as f:
        # Leer todo el contenido del archivo
        data = json.load(f)

        # Inicializar una lista para almacenar los datos
        grabaciones_data = []

        # Iterar sobre los objetos en el archivo JSON
        for entry in data:
            # Extraer los datos de "Record"
            record = entry.get('Record', {})

            # Crear un diccionario con los datos mapeados
            grabacion = {}

            # Crear un ID único
            grabacion['id'] = convert_to_int(record.get('rec_ID', None))  # 'rec_ID' del objeto Record (obligatorio)
            grabacion['ruta_fichero'] = record.get('file', None)  # 'file' del objeto Record (obligatorio)
            grabacion['informe'] = entry.get('_id', None) # '_id' del informe (obligatorio)

            # Verificar si los campos obligatorios (id, ruta_fichero) están presentes
            if grabacion['id'] is None or grabacion['ruta_fichero'] is None or grabacion['informe'] is None:
                continue  # Si falta algún campo obligatorio, la grabación no se agrega

            # Agregar los datos de la grabación a la lista
            grabaciones_data.append(grabacion)

        # Crear el archivo CSV para almacenar los datos
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Definir los encabezados del CSV
            fieldnames = ['id', 'ruta_fichero', 'informe']
            
            # Crear el escritor CSV
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Escribir los encabezados en el CSV
            writer.writeheader()

            # Escribir los datos de las grabaciones en el CSV
            for grabacion in grabaciones_data:
                writer.writerow(grabacion)
                print(f"Registro agregado: {grabacion}")

    print(f"Archivo CSV generado correctamente: {csv_file}")

# Ruta del archivo JSON de entrada y del archivo CSV de salida
json_file = 'sample.json'  # Ajusta la ruta del archivo JSON de entrada
csv_file = 'grabaciones.csv'  # Nombre del archivo CSV de salida

# Ejecutar la función para crear el CSV
create_grabacion_csv(json_file, csv_file)
