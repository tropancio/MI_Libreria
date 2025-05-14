import pandas as pd
import numpy as np
import itertools

def Enumerar(lista):
    """
    genera un listado de los elementos de una lista
    """
    for x,y  in enumerate(lista):
        print(f"{x} {y}")


def listar(lista):
    """
    genera un listado de los elementos de una lista
    """
    for x,y  in enumerate(lista):
        print(f"{x} {y}")



def Comunes(lista1, lista2, nombre="Key"):
    """
    Identifica los elementos comunes y no comunes entre dos
    """
    set1, set2 = set(lista1), set(lista2)
    todos_los_valores = set1 | set2
    reglas = ["OK" if valor in set1 and valor in set2 else "L1" if valor in set1 else "L2" for valor in todos_los_valores]
    
    return pd.DataFrame({nombre: list(todos_los_valores), "Regla": reglas})

def Resumen_columnas(tabla):
    Resumen = pd.DataFrame(columns=["Columna", "Cantidad","Suma", "Elementos"])
    for x in tabla.columns:
        try:
            elemento, cantidad = np.unique(tabla[x].values, return_counts=True)
            try:
                Resumen.loc[len(Resumen)] = [x, len(elemento),int(elemento.sum()),elemento]
            except:
                Resumen.loc[len(Resumen)] = [x, len(elemento),0,elemento]
        except:
            Resumen.loc[len(Resumen)] = [x, 0,0, "Error"]
            
    tipo = tabla.dtypes.reset_index().rename(columns={0:"Tipo","index":"Columna"})
    Resumen = Resumen.merge(tipo,on="Columna",how="left")
    
    return Resumen.sort_values("Cantidad", ascending=False)


# Función para añadir clave y/o índice a una tabla
def Añadir_key_and_Indice(tabla, columna="Key", Key=True, Indice=False, excepciones=[]):

    tabla = tabla.copy()
    if Key:
        columnas_combinadas = [col for col in tabla.columns if col not in excepciones]
        tabla[columna] = tabla[columnas_combinadas].apply(lambda row: ' '.join(row.astype(str)), axis=1)
        tabla[columna] = tabla[columna].str.strip().str.lower()

    if Indice:
        tabla["Indice"] = tabla.groupby(columna).cumcount() + 1
        new_col = f"{columna}2"
        tabla[new_col] = tabla["Indice"].astype(str) + "-" + tabla[columna]
        tabla.drop(columns=["Indice"], inplace=True)
        
    return tabla


# Función para identificar nuevos registros en una tabla comparada con otra
def nuevo_registros(Tabla_nueva, Tabla_antigua):
    col_nueva = Tabla_nueva.columns.values
    col_original = Tabla_antigua.columns.values

    if len(col_nueva) == len(col_original):
        tab_nueva = Añadir_key_and_Indice(Tabla_nueva, Indice=True)
        tab_original = Añadir_key_and_Indice(Tabla_antigua, Indice=True)
        
        l = Comunes(tab_nueva["Key2"], tab_original["Key2"]).rename(columns={"Key": "Key2"})
        new = l[l["Regla"] == "L1"].merge(tab_nueva, on="Key2", how="left")
        return new[col_nueva]
    else:
        print("Tablas distintas")
        return None

def Cruzar_registro(original,nuevo,excepciones=[],method="nuevos"):
    """
    method :
        nuevos -> devuelve los registros nuevos
        iguales -> devuelve los iguales
    """
    columna_original = original.columns
    columna_nuevo = nuevo.columns
    
    original = original.apply(lambda x: x.astype(int) if pd.api.types.is_float_dtype(x) and (x % 1 == 0).all() else x)
    nuevo = nuevo.apply(lambda x: x.astype(int) if pd.api.types.is_float_dtype(x) and (x % 1 == 0).all() else x)

    original = original.apply(lambda x: x.dt.strftime('%d-%m-%Y') if pd.api.types.is_datetime64_dtype(x) else x)
    nuevo = nuevo.apply(lambda x: x.dt.strftime('%d-%m-%Y') if pd.api.types.is_datetime64_dtype(x) else x)
    
    columns = Comunes(columna_original,columna_nuevo)
    excepciones = list(columns[columns["Regla"]!="OK"]["Key"].values)+excepciones
    columnas_final = columns[columns["Regla"]=="OK"]["Key"].values
    
    if len(original)>0:
        original_key = Añadir_key_and_Indice(original,Indice=True,excepciones=excepciones)
        nuevo_key = Añadir_key_and_Indice(nuevo,Indice=True,excepciones=excepciones)
        cruze = Comunes(original_key["Key2"],nuevo_key["Key2"])
        if method == "nuevos":
            registros = cruze[cruze["Regla"]=="L2"]
        elif method == "iguales":
            registros = cruze[cruze["Regla"]=="OK"]
        if len(registros)>0:
            registros = registros.rename(columns={"Key":"Key2"})
            return registros.merge(nuevo_key,on="Key2",how="left").drop(columns=["Key","Key2","Regla"])

        else:
            print("Error registros sin movimientos")
            return cruze
            
    else: 
        return nuevo 


    
def Rellenar_Vacios(Tabla):
    for col in Tabla.columns:
        tipo = Tabla[col].dtype

        if np.issubdtype(tipo, np.number):
            Tabla[col] = Tabla[col].fillna(0)

        elif tipo == object or pd.api.types.is_string_dtype(tipo):
            Tabla[col] = Tabla[col].astype(str)
            Tabla[col] = Tabla[col].fillna("")
        
        elif np.issubdtype(tipo, np.bool_):
            Tabla[col] = Tabla[col].fillna(False)
        
        elif np.issubdtype(tipo, np.datetime64):
            Tabla[col] = Tabla[col].fillna(pd.Timestamp("1900-01-01"))
        
        elif tipo == object or pd.api.types.is_string_dtype(tipo):
            Tabla[col] = Tabla[col].fillna("")
        
        else:
            print(f"Tipo no manejado: {col} ({tipo}) — sin modificar")
    
    return Tabla


def Resumir(Tabla,Agrup,Suma=None):
    if Suma:
        return Tabla.groupby([Agrup]).agg(can=(Agrup,"count"),suma=(Suma,"sum")).reset_index()
    else:
        return Tabla.groupby([Agrup]).agg(can=(Agrup,"count")).reset_index()


def Cruzar_Diferencias(tab1,tab2):
    ll = Comunes(tab1.columns,tab2.columns)
    OK = ll[ll["Regla"]=="OK"]
    L1 = ll[ll["Regla"]=="L1"]
    L2 = ll[ll["Regla"]=="L2"]
    
    ll = Resumen_columnas(tab1[OK["Key"]]).merge(Resumen_columnas(tab2[OK["Key"]]),on="Columna",how="outer")
    ll["Dif_Cantidad"] = ll["Cantidad_x"]-ll["Cantidad_y"]
    ll["Dif_Suma"] = ll["Suma_x"]-ll["Suma_y"]
    ll["Dif_Suma"] = ll["Suma_x"]-ll["Suma_y"]
    ll["Dif"] = ll["Dif_Cantidad"]+ll["Dif_Suma"]
    return ll
