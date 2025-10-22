import json
import csv

from conversiones import convert_to_date_matriculacion

# Función para crear un CSV desde un archivo JSON con los atributos específicos
def create_vehiculo_csv(json_file, csv_file):
    with open(json_file, 'r', encoding='latin1') as f:
        # Leer todo el contenido del archivo
        data = json.load(f)

        # Inicializar una lista para almacenar los datos
        vehiculos_data = []

        # Iterar sobre los objetos en el archivo JSON
        for entry in data:
            # Extraer los datos de "vehicle"
            vehicle = entry.get('vehicle', {})
            owner = vehicle.get('Owner', {})

            # Crear un diccionario con los datos mapeados
            vehiculo = {}

            # Mapear los atributos
            vehiculo['matricula'] = vehicle.get('number plate', None)  # 'vehicle.number_plate'
            vehiculo['bastidor'] = vehicle.get('chassis number', None)  # 'vehicle.chassis_number'
            vehiculo['marca'] = vehicle.get('make', None)  # 'vehicle.make'
            vehiculo['modelo'] = vehicle.get('model', None)  # 'vehicle.model'
            vehiculo['potencia'] = vehicle.get('power', None)  # 'vehicle.power'
            vehiculo['color'] = vehicle.get('colour', None)  # 'vehicle.colour'
            vehiculo['fecha_matriculacion'] = convert_to_date_matriculacion(vehicle.get('registry date', None))  # 'vehicle.registry_date'
            vehiculo['titular'] = owner.get('DNI', None)  # 'vehicle.Owner.DNI'

            # Verificar si el campo obligatorio 'matricula' está presente
            if vehiculo['matricula'] is None:
                continue  # Si falta la matrícula, se omite el registro

            # Agregar los datos del vehículo a la lista
            vehiculos_data.append(vehiculo)

        # Crear el archivo CSV para almacenar los datos
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Definir los encabezados del CSV
            fieldnames = [
                'matricula', 'bastidor', 'marca', 'modelo', 'potencia',
                'color', 'fecha_matriculacion', 'titular'
            ]
            
            # Crear el escritor CSV
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Escribir los encabezados en el CSV
            writer.writeheader()

            # Escribir los datos de los vehículos en el CSV
            for vehiculo in vehiculos_data:
                writer.writerow(vehiculo)
                print(f"Registro agregado: {vehiculo}")

    print(f"Archivo CSV generado correctamente: {csv_file}")

# Ruta del archivo JSON de entrada y del archivo CSV de salida
json_file = 'sample.json'  # Ajusta la ruta del archivo JSON de entrada
csv_file = 'vehiculo.csv'  # Nombre del archivo CSV de salida

# Ejecutar la función para crear el CSV
create_vehiculo_csv(json_file, csv_file)
