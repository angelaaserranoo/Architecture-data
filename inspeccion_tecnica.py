import json
import csv

from conversiones import convert_to_date

# Función para crear un CSV desde un archivo JSON con los atributos específicos
def create_inspeccion_tecnica_csv(json_file, csv_file):
    with open(json_file, 'r', encoding='latin1') as f:
        # Leer todo el contenido del archivo
        data = json.load(f)

        # Inicializar una lista para almacenar los datos
        inspecciones_data = []

        # Iterar sobre los objetos en el archivo JSON
        for entry in data:
            # Extraer los datos de "vehicle"
            vehicle = entry.get('vehicle', {})
            roadworthiness = vehicle.get('roadworthiness', [])

            # Crear un diccionario con los datos mapeados
            inspeccion = {}

            # Obtener la matrícula del vehículo
            inspeccion['id_matricula'] = vehicle.get('number plate', None)  # 'vehicle/number_plate'

            # Verificar si el campo obligatorio 'id_matricula' está presente
            if inspeccion['id_matricula'] is None or not roadworthiness:
                continue  # Si falta la matrícula o no hay inspecciones técnicas, se omite el registro

            # Verificar el formato de 'roadworthiness'
            if isinstance(roadworthiness, list):  # Si es una lista de inspecciones
                # Obtener la inspección más reciente basada en la fecha
                latest_inspection = max(
                    roadworthiness,
                    key=lambda x: x.get('MOT date', '')  # Obtener el valor más reciente por 'MOT date'
                )

                # Mapear los campos de la inspección más reciente
                inspeccion['fecha'] = convert_to_date(latest_inspection.get('MOT date', None))
                inspeccion['observaciones'] = ", ".join(latest_inspection.get('shortcomings', []))
                
                # Si no hay observaciones en la inspección más reciente
                if not inspeccion['observaciones']:
                    inspeccion['observaciones'] = "No se especificaron observaciones"

            elif isinstance(roadworthiness, str):  # Si es una cadena con una sola fecha
                inspeccion['fecha'] = convert_to_date(roadworthiness)  # Usar la fecha directamente
                inspeccion['observaciones'] = "No se especificaron observaciones"

            # Agregar los datos de la inspección a la lista
            inspecciones_data.append(inspeccion)

        # Crear el archivo CSV para almacenar los datos
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Definir los encabezados del CSV
            fieldnames = ['id_matricula', 'fecha', 'observaciones']
            
            # Crear el escritor CSV
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Escribir los encabezados en el CSV
            writer.writeheader()

            # Escribir los datos de las inspecciones en el CSV
            for inspeccion in inspecciones_data:
                writer.writerow(inspeccion)
                print(f"Registro agregado: {inspeccion}")

    print(f"Archivo CSV generado correctamente: {csv_file}")

# Ruta del archivo JSON de entrada y del archivo CSV de salida
json_file = 'sample.json'  # Ajusta la ruta del archivo JSON de entrada
csv_file = 'inspeccion_tecnica.csv'  # Nombre del archivo CSV de salida

# Ejecutar la función para crear el CSV
create_inspeccion_tecnica_csv(json_file, csv_file)
