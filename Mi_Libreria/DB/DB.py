
import pyodbc
import pandas as pd
import shutil


def get_conn(path=r"C:\Users\MaximilianoAlarcon\Desktop\DJMax\Data.accdb"):
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


def get_connecciones(conn):    
    """ 
    """
    connecciones = []
    cursor = conn.cursor()
    todo = pd.DataFrame(data = [list(x) for x in cursor.tables()],columns=['RUTA','TIPO','NOMBRE','SCHEMA',"PROPERTY"])
    todo = todo[todo['SCHEMA'] == 'SYNONYM']
    cursor.close()
    return todo


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
    try:
        cursor = conn.cursor()
        columnas = df.columns
        registro = list(df.itertuples(index=False,name = None))

        par1 = " , ".join(columnas)
        par2 = " , ".join(["?" for x in columnas])
        
        query = f"INSERT INTO {Tabla} ({par1}) VALUES ({par2})"
        cursor.executemany(query, registro)
        cursor.commit()
        cursor.close()

        return True
    
    except Exception as e:
        print(e)
        return False



def copy_accdb(destino):
    """
    Copia el archivo de base de datos a la ruta especificada.
    """
    originall = r".\black.accdb"
    shutil.copy2(originall, destino)
    print(f"Archivo copiado a {destino}")


def get_tablas(conn, filtro:str = "TABLE"):
    cursor = conn.cursor()
    tablas = [x for x in cursor.tables() if x.table_type == filtro]
    cursor.close()
    return tablas




def generar_tabla(conn, tabla,campos:pd.DataFrame) -> bool:

    mapa_tipos = {
        "string[python]": "TEXT",
        "float64": "DOUBLE",
        "datetime64[ns]": "DATETIME",
        "int64": "INTEGER"
    }

    campos["tipo_origen"] = campos["tipo_origen"].astype(str)

    if not {'nombre', 'tipo_origen'}.issubset(campos.columns):
        raise ValueError("El DataFrame debe tener columnas: 'nombre' y 'tipo_origen'")

    campos["tipo_origen"] = campos["tipo_origen"].map(mapa_tipos).fillna("TEXT")
    columnas_sql = ",\n    ".join([f"[{row['nombre']}] {row['tipo_origen']}" for _, row in campos.iterrows()])

    sql_principal = f"CREATE TABLE [{tabla}] (\n    ID AUTOINCREMENT PRIMARY KEY,  \n    {columnas_sql}\n);"
    
    return Ejecutar(conn,sql_principal)



def generar_tabla_dcs(conn, tabla, df: pd.DataFrame, _desc:bool = True) -> dict:
    sql_documentacion = f"CREATE TABLE [{tabla}_desc] (\n    [nombre] TEXT,\n    [tipo_origen] TEXT,\n    [extra] TEXT);"

    columnas = df.dtypes.reset_index().rename(columns={"index": "nombre", 0: "tipo_origen"})

    sql1,sql2,sql3,sql4 = False, False, False, False

    try:
        sql1 = generar_tabla(conn, tabla, columnas)
        sql2 = Cargar_Data_DB(conn,f"{tabla}", df)
        
        if _desc:
            sql3 = Ejecutar(conn, sql_documentacion)
            sql4 = Cargar_Data_DB(conn,f"{tabla}_desc", columnas[["nombre", "tipo_origen"]])

    except Exception as e:
        print(e)

    return {
        "crear_tabla": "Creada" if sql1 else "Error al crear tabla",
        "insertar_tabas": "Insertada" if sql2 else "Error al insertar data",
        "crear_documentacion": "Creada" if sql3 else "Error al crear tabla",
        "insertar_documentacion": "Insertada" if sql4 else "Error al insertar data"
    }


def actualizar_tabla(conn,tabla:str,set:str,id:list):
    
    """
    Ejemplo
    tabla : tabla_banco
    set: DESCRIPTION = 'Transferencia via CCA'
    id : [156, 165, 168, 170, 175, 176, 177]
    """

    try:
        cursor = conn.cursor()
        ids = "(" + ",".join(str(x) for x in id) + ")"
        cursor.execute(f" UPDATE {tabla} SET {set} WHERE ID IN {ids}")
        cursor.commit()
        cursor.close()
        return True
    
    except Exception as e:
        print(e)
        return False