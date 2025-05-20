
import pyodbc
import pandas as pd
import numpy as np

def Cargar_Data_DB(conn,Tabla,df):
    cursor = conn.cursor()
    columnas = df.columns
    registro = list(df.itertuples(index=False,name = None))

    par1 = " , ".join(columnas)
    par2 = " , ".join(["?" for x in columnas])
    
    query = f"INSERT INTO {Tabla} ({par1}) VALUES ({par2})"
    cursor.executemany(query, registro)
    cursor.commit()
    cursor.close()