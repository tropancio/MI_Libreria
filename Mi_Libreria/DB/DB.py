
import pyodbc
import pandas as pd
import shutil


def get_conn(path=r"C:\Users\MaximilianoAlarcon\Desktop\DJMax\Data.accdb"):

    """
    path=
    Devulve un conn de la ruta indicada
    """

    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        rf'DBQ={path};'
    )    
    conn = pyodbc.connect(conn_str)
    return conn 


def Ejecutar(conn,query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        cursor.commit()
        cursor.close()
        return True
    
    except Exception as e:
        print(e)
        return False


def Consultas(conn, query):
    """
    Ejecuta una consulta SQL y devuelve los resultados en un DataFrame.
    """
    cursor = conn.cursor()
    cursor.execute(query)
    columnas = [col[0] for col in cursor.description]
    datos = cursor.fetchall()
    df = pd.DataFrame([list(x) for x in datos], columns=columnas)
    cursor.close()
    return df


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


def copy_accdb(destino):
    """
    Copia el archivo de base de datos a la ruta especificada.
    """
    originall = r".\black.accdb"
    shutil.copy2(originall, destino)
    print(f"Archivo copiado a {destino}")

def get_tablas(conn):
    cursor = conn.cursor()
    tablas = [x for x in cursor.tables() if x.table_type == 'TABLE']
    cursor.close()
    return tablas



    
