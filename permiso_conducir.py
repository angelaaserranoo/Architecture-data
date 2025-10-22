import json
import csv
import uuid  # Para generar un ID único

from conversiones import convert_to_date

# Función para crear un CSV desde un archivo JSON con los atributos de "PermisoConducir"
def create_permiso_conducir_csv(json_file, csv_file):
    with open(json_file, 'r', encoding='latin1') as f:
        # Leer todo el contenido del archivo
        data = json.load(f)

        # Inicializar una lista para almacenar los datos
        permisos_data = []

        # Iterar sobre los objetos en el archivo JSON
        for entry in data:
            # Extraer los datos de "Driver" y su "driving license"
            driver = entry.get('vehicle', {}).get('Driver', {})
            driving_license = driver.get('driving license', {})

            # Crear un diccionario con los datos mapeados
            permiso = {}

            # Obtener los datos obligatorios
            permiso['id_conductor'] = driver.get('DNI', None)  # 'DNI' del Driver (obligatorio)
            permiso['tipo'] = driving_license.get('type', None)  # 'type' del driving license
            permiso['fecha expedición'] = convert_to_date(driving_license.get('date', None))  # 'date' del driving license

            # Verificar si el campo obligatorio 'id_conductor' está presente
            if permiso['id_conductor'] is None:
                continue  # Si falta el DNI, la entrada no se agrega

            # Agregar los datos del permiso a la lista
            permisos_data.append(permiso)

        # Crear el archivo CSV para almacenar los datos
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Definir los encabezados del CSV
            fieldnames = ['id_conductor', 'tipo', 'fecha expedición']
            
            # Crear el escritor CSV
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Escribir los encabezados en el CSV
            writer.writeheader()

            # Escribir los datos de los permisos en el CSV
            for permiso in permisos_data:
                writer.writerow(permiso)
                print(f"Registro agregado: {permiso}")

    print(f"Archivo CSV generado correctamente: {csv_file}")

# Ruta del archivo JSON de entrada y del archivo CSV de salida
json_file = 'sample.json'  # Ajusta la ruta del archivo JSON de entrada
csv_file = 'permiso_conducir.csv'  # Nombre del archivo CSV de salida

# Ejecutar la función para crear el CSV
create_permiso_conducir_csv(json_file, csv_file)
