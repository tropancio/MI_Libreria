import pyodbc
import pandas as pd
import shutil
import os
from contextlib import contextmanager

class DatabaseConnection:
    """Database connection manager for Microsoft Access"""
    def __init__(self, database_path=None):
        # Default database path if not provided
        if database_path is None:
            database_path = os.path.join(os.path.dirname(__file__), "black.accdb")
        self.database_path = database_path
    
    def get_connection_string(self) -> str:
        """Get the database connection string"""
        # Ensure absolute path
        db_path = os.path.abspath(self.database_path)
        return (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
        )
    
    def get_connection(self) -> pyodbc.Connection:
        """Get a database connection"""
        try:
            # Verify database file exists
            db_path = os.path.abspath(self.database_path)
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Database file not found: {db_path}")
            
            conn_str = self.get_connection_string()
            connection = pyodbc.connect(conn_str)

            return connection
        except Exception as e:
            raise
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        connection = None
        try:
            connection = self.get_connection()
            yield connection
        except Exception as e:
            if connection:
                try:
                    connection.rollback()
                except:
                    pass
                
            raise
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass

    def ejecutar(self, conn, query) -> dict:
        """Ejecuta una consulta SQL que no retorna datos (INSERT, UPDATE, DELETE)"""
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            rows_affected = cursor.rowcount
            cursor.commit()
            cursor.close()

            return {
                "status": True,
                "message": "Query executed successfully",
                "rows_affected": rows_affected
            }
        
        except Exception as e:
            print("[❌] Error al ejecutar consulta")
            return {
                "status": False,
                "message": str(e)
            }

    def get_conexiones(self, conn):
        """Obtiene las conexiones de la base de datos"""
        conexiones = []
        cursor = conn.cursor()
        todo = pd.DataFrame(data=[list(x) for x in cursor.tables()], 
                          columns=['RUTA', 'TIPO', 'NOMBRE', 'SCHEMA', "PROPERTY"])
        todo = todo[todo['SCHEMA'] == 'SYNONYM']
        cursor.close()
        return todo

    def consultas(self, conn, query):
        """Ejecuta una consulta SQL y devuelve los resultados en un DataFrame"""
        cursor = conn.cursor()
        cursor.execute(query)
        columnas = [col[0] for col in cursor.description]
        datos = cursor.fetchall()
        df = pd.DataFrame([list(x) for x in datos], columns=columnas)
        cursor.close()
        return df

    def cargar_data_db(self, conn, tabla, df):
        """Carga datos de un DataFrame a una tabla de la base de datos"""
        try:
            cursor = conn.cursor()
            columnas = df.columns
            registro = list(df.itertuples(index=False, name=None))

            par1 = " , ".join(columnas)
            par2 = " , ".join(["?" for x in columnas])
            
            query = f"INSERT INTO {tabla} ({par1}) VALUES ({par2})"
            cursor.executemany(query, registro)
            cursor.commit()
            cursor.close()

            return True
        except Exception as e:
            print(e)
            return False

    def copy_accdb(self, destino):
        """Copia el archivo de base de datos a la ruta especificada"""
        original = r".\black.accdb"
        shutil.copy2(original, destino)
        print(f"Archivo copiado a {destino}")

    def get_tablas(self, conn, filtro: str = "TABLE"):
        """Obtiene las tablas de la base de datos"""
        cursor = conn.cursor()
        tablas = [x for x in cursor.tables() if x.table_type == filtro]
        cursor.close()
        return tablas

    def generar_tabla(self, conn, tabla, campos: pd.DataFrame) -> bool:
        """Genera una nueva tabla en la base de datos"""
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
        
        return self.ejecutar(conn, sql_principal).get("status", False)

    def generar_tabla_dcs(self, conn, tabla, df: pd.DataFrame, _desc: bool = True) -> dict:
        """Genera una tabla con su documentación"""
        sql_documentacion = f"CREATE TABLE [{tabla}_desc] (\n    [nombre] TEXT,\n    [tipo_origen] TEXT,\n    [extra] TEXT,\n    [CATEGORICA] TEXT);"

        columnas = df.dtypes.reset_index().rename(columns={"index": "nombre", 0: "tipo_origen"})

        sql1, sql2, sql3, sql4 = False, False, False, False

        try:
            sql1 = self.generar_tabla(conn, tabla, columnas)
            sql2 = self.cargar_data_db(conn, f"{tabla}", df)
            
            if _desc:
                sql3 = self.ejecutar(conn, sql_documentacion).get("status", False)
                sql4 = self.cargar_data_db(conn, f"{tabla}_desc", columnas[["nombre", "tipo_origen"]])

        except Exception as e:
            print(e)

        return {
            "crear_tabla": "Creada" if sql1 else "Error al crear tabla",
            "insertar_tabas": "Insertada" if sql2 else "Error al insertar data",
            "crear_documentacion": "Creada" if sql3 else "Error al crear tabla",
            "insertar_documentacion": "Insertada" if sql4 else "Error al insertar data"
        }

    def actualizar_tabla(self, conn, tabla: str, set_clause: str, id_list: list):
        """Actualiza registros en una tabla basado en una lista de IDs
        
        Ejemplo:
        tabla: 'tabla_banco'
        set_clause: "DESCRIPTION = 'Transferencia via CCA'"
        id_list: [156, 165, 168, 170, 175, 176, 177]
        """

        ids = "(" + ",".join(str(x) for x in id_list) + ")"
        query = f" UPDATE {tabla} SET {set_clause} WHERE ID IN {ids}"
        return self.ejecutar(conn, query)
        



# For backward compatibility - function-based interface
def get_connection() -> pyodbc.Connection:
    """Get a database connection (backward compatibility)"""
    db = DatabaseConnection()
    return db.get_connection()

def get_conn(path):
    """Get a database connection with custom path (backward compatibility)"""
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        rf'DBQ={path};'
    )  
    conn = pyodbc.connect(conn_str)
    return conn 

def Ejecutar(conn, query):
    """Ejecuta una consulta SQL (backward compatibility)"""
    db = DatabaseConnection()
    return db.ejecutar(conn, query)

def get_connecciones(conn):
    """Obtiene conexiones (backward compatibility)"""
    db = DatabaseConnection()
    return db.get_conexiones(conn)

def Consultas(conn, query):
    """Ejecuta consultas (backward compatibility)"""
    db = DatabaseConnection()
    return db.consultas(conn, query)

def Cargar_Data_DB(conn, tabla, df):
    """Carga datos (backward compatibility)"""
    db = DatabaseConnection()
    return db.cargar_data_db(conn, tabla, df)

def copy_accdb(destino):
    """Copia base de datos (backward compatibility)"""
    db = DatabaseConnection()
    return db.copy_accdb(destino)

def get_tablas(conn, filtro: str = "TABLE"):
    """Obtiene tablas (backward compatibility)"""
    db = DatabaseConnection()
    return db.get_tablas(conn, filtro)

def generar_tabla(conn, tabla, campos: pd.DataFrame) -> bool:
    """Genera tabla (backward compatibility)"""
    db = DatabaseConnection()
    return db.generar_tabla(conn, tabla, campos)

def generar_tabla_dcs(conn, tabla, df: pd.DataFrame, _desc: bool = True) -> dict:
    """Genera tabla con documentación (backward compatibility)"""
    db = DatabaseConnection()
    return db.generar_tabla_dcs(conn, tabla, df, _desc)

def actualizar_tabla(conn, tabla: str, set_clause: str, id_list: list):
    """Actualiza tabla (backward compatibility)"""
    db = DatabaseConnection()
    return db.actualizar_tabla(conn, tabla, set_clause, id_list)
