import json
import csv

from conversiones import convert_to_date
from conversiones import convert_to_boolean
from conversiones import convert_to_int

# Función para crear un CSV desde un archivo JSON con los atributos específicos
def create_sancion_csv(json_file, csv_file):
    with open(json_file, 'r', encoding='latin1') as f:
        # Leer todo el contenido del archivo
        data = json.load(f)

        # Inicializar una lista para almacenar los datos
        sanciones_data = []

        # Iterar sobre los objetos en el archivo JSON
        for entry in data:
            # Extraer los datos de "Speed_ticket"
            speed_ticket = entry.get('Speed ticket', {})
            debtor = speed_ticket.get('Debtor', {})
            
            # Crear un diccionario con los datos mapeados
            sancion = {}

            # Mapear los campos requeridos
            sancion['id'] = entry.get('_id', None)  # '_id' del objeto (obligatorio)

            sancion['fecha_emision'] = convert_to_date(speed_ticket.get('Issue date', None))  # 'Speed_ticket.Issue_date' (obligatorio)
            sancion['fecha_pago'] = convert_to_date(speed_ticket.get('Pay date', None))  # 'Speed_ticket.Pay_date'
            sancion['cantidad'] = convert_to_int(speed_ticket.get('Amount', None))  # 'Speed_ticket.Amount' (obligatorio)
            sancion['tipo_moneda'] = speed_ticket.get('Currency', None)  # 'Speed_ticket.Currency' (obligatorio)
            sancion['metodo_pago'] = speed_ticket.get('Pay type', None)  # 'Speed_ticket.Pay_type'
            sancion['estado'] = speed_ticket.get('State', None)  # 'Speed_ticket.State' (obligatorio)
            sancion['deudor'] = debtor.get('DNI', None)  # 'Speed_ticket.Debtor.DNI' (obligatorio)
            sancion['deudor_insolvente'] = convert_to_boolean(debtor.get('Insolvency', None))  # 'Speed_ticket.Debtor.Insolvency' (obligatorio)

            # Verificar si los campos obligatorios están presentes
            if sancion['id'] is None or sancion['fecha_emision'] is None or sancion['cantidad'] is None or \
                sancion['tipo_moneda'] is None or sancion['estado'] is None or sancion['deudor'] is None \
                or sancion['deudor_insolvente'] is None    :
                continue  # Si falta algún campo obligatorio, la sanción no se agrega

            # Agregar los datos de la sanción a la lista
            sanciones_data.append(sancion)

        # Crear el archivo CSV para almacenar los datos
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Definir los encabezados del CSV
            fieldnames = [
                'id', 'fecha_emision', 'fecha_pago', 'cantidad', 
                'tipo_moneda', 'metodo_pago', 'estado', 'deudor', 'deudor_insolvente'
            ]
            
            # Crear el escritor CSV
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Escribir los encabezados en el CSV
            writer.writeheader()

            # Escribir los datos de las sanciones en el CSV
            for sancion in sanciones_data:
                writer.writerow(sancion)
                print(f"Registro agregado: {sancion}")

    print(f"Archivo CSV generado correctamente: {csv_file}")

# Ruta del archivo JSON de entrada y del archivo CSV de salida
json_file = 'sample.json'  # Ajusta la ruta del archivo JSON de entrada
csv_file = 'sancion.csv'  # Nombre del archivo CSV de salida

# Ejecutar la función para crear el CSV
create_sancion_csv(json_file, csv_file)
