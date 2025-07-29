# Initialization file for Principal module

# Import the main class and all compatibility functions
from .Principal import (
    DataProcessor,
    Enumerar,
    Numeros,
    Extraer_numeros,
    Valores_Numericos,
    convertir_columnas,
    Renombrar_columnas,
    Comunes,
    Resumen_columnas,
    Añadir_key_and_Indice,
    nuevo_registros,
    Cruzar_registro,
    Rellenar_Vacios,
    Resumir,
    Cruzar_Diferencias
)

# Export everything
__all__ = [
    'DataProcessor',
    'Enumerar',
    'Numeros',
    'Extraer_numeros',
    'Valores_Numericos',
    'convertir_columnas',
    'Renombrar_columnas',
    'Comunes',
    'Resumen_columnas',
    'Añadir_key_and_Indice',
    'nuevo_registros',
    'Cruzar_registro',
    'Rellenar_Vacios',
    'Resumir',
    'Cruzar_Diferencias'
]
