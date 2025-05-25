
import pyodbc
import pandas as pd



def get_conn(path=r"C:\Users\MaximilianoAlarcon\Desktop\DJMax\Data.accdb"):
    """
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
    df = pd.DataFrame(datos, columns=columnas)
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