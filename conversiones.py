from datetime import datetime
import re

# Función para convertir una fecha en texto al formato DATE (YYYY-MM-DD)
def convert_to_date(value):
    try:
        # Ajustar el formato de entrada (DD/MM/YYYY) y convertir al formato DATE (YYYY-MM-DD)
        return datetime.strptime(value, '%d/%m/%Y').date()
    except (ValueError, TypeError):
        return None

def convert_to_date_matriculacion(value):
    try:
        # Limpiar sufijos como TH, ST, ND, RD usando una expresión regular
        value_cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', value.lower())
        # Convertir al formato estándar
        return datetime.strptime(value_cleaned, '%A %d of %B, %Y').date()
    except (ValueError, TypeError):
        return None


# Función para convertir valores a booleano
def convert_to_boolean(value):
    if isinstance(value, str):
        value = value.strip().lower()  # Normalizar el texto
        return value in ['si', 'true', '1', 'yes']
    return bool(value)


# Función para convertir valores a enteros
def convert_to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None