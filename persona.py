import json
import csv

from conversiones import convert_to_date
from conversiones import convert_to_int

# Función para crear un CSV desde un archivo JSON con los atributos de "persona"
def create_persona_csv(json_file, csv_file):
    # Crear un conjunto para rastrear los DNIs ya vistos
    dnis_vistos = set()

    with open(json_file, 'r', encoding='latin1') as f:
        # Leer todo el contenido del archivo
        data = json.load(f)

        # Inicializar una lista para almacenar los datos
        personas_data = []

        # Iterar sobre los objetos en el archivo JSON
        for entry in data:
            # Extraer los datos de "driver" y "owner"
            driver = entry.get('vehicle', {}).get('Driver', {})
            owner = entry.get('vehicle', {}).get('Owner', {})

            # Función para extraer la información común de "driver" y "owner"
            def obtener_persona(persona):
                return {
                    'dni': persona.get('DNI', None),  # 'DNI' (obligatorio)
                    'nombre': persona.get('Name', None),  # 'Name' (obligatorio)
                    'apellido1': persona.get('Surname', None),  # 'Surname'
                    'apellido2': persona.get('Sec_Surname', None),  # 'Sec_Surname'
                    'direccion': persona.get('Address', None),  # 'Address'
                    'localidad': persona.get('Town', None),  # 'Town'
                    'email': persona.get('Email', None),  # 'Email'
                    'telefono': convert_to_int(persona.get('Phone number', None)),  # 'Phone'
                    'fecha_nacimiento': convert_to_date(persona.get('Birthdate', None))  # 'Birthdate' (obligatorio)
                }

            # Obtener la información de driver y owner
            personas = [obtener_persona(driver), obtener_persona(owner)]

            # Procesar cada persona (driver y owner)
            for persona in personas:
                # Verificar si el DNI ya ha sido visto
                if persona['dni'] in dnis_vistos or persona['dni'] is None:
                    continue  # Si el DNI ya ha sido visto o es None, no agregarlo

                # Agregar el DNI al conjunto de DNIs ya vistos
                dnis_vistos.add(persona['dni'])

                # Agregar la persona a la lista de datos
                personas_data.append(persona)

        # Crear el archivo CSV para almacenar los datos
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Definir los encabezados del CSV
            fieldnames = ['dni', 'nombre', 'apellido1', 'apellido2', 'direccion', 'localidad', 'email', 'telefono', 'fecha_nacimiento']
            
            # Crear el escritor CSV
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Escribir los encabezados en el CSV
            writer.writeheader()

            # Escribir los datos de las personas en el CSV
            for persona in personas_data:
                writer.writerow(persona)
                print(f"Registro agregado: {persona}")

    print(f"Archivo CSV generado correctamente: {csv_file}")

# Ruta del archivo JSON de entrada y del archivo CSV de salida
json_file = 'sample.json'  # Ajusta la ruta del archivo JSON de entrada
csv_file = 'personas.csv'  # Nombre del archivo CSV de salida

# Ejecutar la función para crear el CSV
create_persona_csv(json_file, csv_file)
