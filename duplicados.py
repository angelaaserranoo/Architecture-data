import csv

def verificar_unicidad(csv_file):
    # Crear un conjunto para rastrear los IDs ya vistos
    ids_vistos = set()

    # Abrir el archivo CSV
    with open(csv_file, mode='r', encoding='utf-8') as csvfile:
        # Crear un lector CSV
        reader = csv.DictReader(csvfile)

        # Recorrer cada fila del CSV
        for row in reader:
            # Obtener el id de la fila actual
            id_actual = row['id']

            # Comprobar si el id ya está en el conjunto
            if id_actual in ids_vistos:
                # Si el id ya fue visto, imprimir un mensaje de alerta
                print(f"Alerta: ID duplicado encontrado: {id_actual}")
            else:
                # Si es único, agregarlo al conjunto
                ids_vistos.add(id_actual)
        print("fin")

# Ruta del archivo CSV
csv_file = 'grabaciones.csv'  # Ajusta la ruta del archivo CSV

# Ejecutar la función
verificar_unicidad(csv_file)
