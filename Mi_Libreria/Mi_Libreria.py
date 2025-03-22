import pandas as pd
import numpy as np
import itertools

def Resumen_columnas(tabla):
    Resumen = pd.DataFrame(columns=["Columna", "Cantidad", "Elementos"])
    for x in tabla.columns:
        try:
            elemento, cantidad = np.unique(tabla[x].values, return_counts=True)
            Resumen.loc[len(Resumen)] = [x, len(elemento), elemento]
        except:
            Resumen.loc[len(Resumen)] = [x, 0, "Error"]
    print(
        "hola"
    )
    return Resumen.sort_values("Cantidad", ascending=False)


# Función para añadir clave y/o índice a una tabla
def Añadir_key_and_Indice(tabla, columna="Key", Key=True, Indice=False):
    tabla = tabla.copy()
    if Key:
        tabla[columna] = tabla.apply(lambda row: ' '.join(row.astype(str)), axis=1)
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
    
    #Comit

