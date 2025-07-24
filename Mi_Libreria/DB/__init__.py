import pyodbc
import pandas as pd

# Import the main class
from .DB import DatabaseConnection

# Export the main class
__all__ = [
    'DatabaseConnection',
    'get_connection',
    'get_conn', 
    'Ejecutar',
    'get_connecciones',
    'Consultas',
    'Cargar_Data_DB',
    'copy_accdb',
    'get_tablas',
    'generar_tabla',
    'generar_tabla_dcs',
    'actualizar_tabla'
]
