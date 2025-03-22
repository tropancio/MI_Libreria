import pandas as pd
import numpy as np
import itertools


def lista_Indice(lista_original):
    lista_con_Indice = []
    volatil = []
    for elemento in lista_original:
        volatil.append(elemento)
        nuevo_indice = volatil.count(elemento)*100000 + elemento
        lista_con_Indice.append(nuevo_indice)
    return lista_con_Indice

def Combinacion(df_base, grupo, Cruze):
    combi = list(itertools.combinations(df_base["Id_y"].astype(str).values, grupo))
    combi2 = ["-".join(tupla) for tupla in combi]
    combi3 = pd.DataFrame([[x] + x.split("-") for x in combi2])
    combi4 = pd.melt(combi3, id_vars=[0], var_name="Atributo", value_name="Id_y")
    combi4["Id_y"] = combi4["Id_y"].astype(int)
    df_merge = pd.merge(combi4[[0, "Id_y"]], df_base, on="Id_y", how="left")
    df_resumen = df_merge.groupby(0)[Cruze].agg(["sum"]).reset_index()
    df_resumen["sum_1"] = lista_Indice(df_resumen["sum"].values)
    df_final = pd.merge(df_merge, df_resumen, on=0, how="left")
    return df_final

def Procesador(data1, data2, Cruze, tolerancia):
    data1 = data1.copy()
    data2 = data2.copy()
    data1.loc[:, f"{Cruze}_Indice"] = lista_Indice(data1[Cruze])
    data2.loc[:, f"{Cruze}_Indice"] = lista_Indice(data2[Cruze])
    data1.loc[:, f"{Cruze}_Indice"] = data1[f"{Cruze}_Indice"].astype(float)
    data2.loc[:, f"{Cruze}_Indice"] = data2[f"{Cruze}_Indice"].astype(float)
    data1 = data1.sort_values(by=f"{Cruze}_Indice").copy()
    data2 = data2.sort_values(by=f"{Cruze}_Indice").copy()
    
    Resultado = pd.merge_asof(
        data1, 
        data2, 
        on=f"{Cruze}_Indice", 
        direction="nearest", 
        tolerance=tolerancia
    )

    for y in range(2, 10):
        mask_no_clasif = ~data2["Id_y"].isin(Resultado["Id_y"].values)
        Sin_Clasificar = data2[mask_no_clasif]
        x = y if y != 4 else Sin_Clasificar.shape[0]
        if Sin_Clasificar.shape[0] >= x and x >= 2:
            Resultado_comb = Combinacion(Sin_Clasificar, x, Cruze)
            Resultado_comb = Resultado_comb.rename(
                columns={f"{Cruze}_Indice": "Eliminar1", "sum_1": f"{Cruze}_Indice"}
            )
            No_Encontrado = data1[
                data1["Id_x"].isin(Resultado.loc[pd.isna(Resultado["Id_y"]), "Id_x"].values)
            ].copy()
            No_Encontrado.loc[:, f"{Cruze}_Indice"] = No_Encontrado[f"{Cruze}_Indice"].astype(float)
            Resultado_comb.loc[:, f"{Cruze}_Indice"] = Resultado_comb[f"{Cruze}_Indice"].astype(float)
            No_Encontrado = No_Encontrado.sort_values(by=f"{Cruze}_Indice").copy()
            Resultado_comb = Resultado_comb.sort_values(by=f"{Cruze}_Indice").copy()
            Encontrado1 = pd.merge_asof(
                No_Encontrado, 
                Resultado_comb, 
                on=f"{Cruze}_Indice", 
                direction="nearest", 
                tolerance=tolerancia
            )
            columnas_base = list(Encontrado1.columns)
            if 0 in columnas_base:
                columnas_base = columnas_base[:columnas_base.index(0) + 1]
            
            
            Encontrado1 = pd.merge(
                Encontrado1[columnas_base], 
                Resultado_comb, 
                on=0, 
                how="left"
            )
            R_clasificados = Resultado.loc[~pd.isna(Resultado["Id_y"])]
            if not R_clasificados.empty:
                Resultado_final = pd.concat([R_clasificados, Encontrado1], ignore_index=True)
            else:
                Resultado_final = Encontrado1
            # En vez de forzar columnas_resultado, dejamos todo:
            Resultado = Resultado_final
    return Resultado

def Proceso(data1, data2, Cruze, Agrupacion="", tolerancia=0):
    data1 = data1.copy()
    data2 = data2.copy()
    data1.loc[:, "Id_x"] = range(1, data1.shape[0] + 1)
    data2.loc[:, "Id_y"] = range(1, data2.shape[0] + 1)
    if not Agrupacion:
        Todos = Procesador(data1, data2, Cruze, tolerancia)
    else:
        lista_resultados = []
        for valor_grupo in np.unique(data1[Agrupacion].values):
            df1_subset = data1[data1[Agrupacion] == valor_grupo].copy()
            df2_subset = data2[data2[Agrupacion] == valor_grupo].copy()
            if df1_subset.shape[0]>0 and df2_subset.shape[0]>0:
                resultado_parcial = Procesador(df1_subset, df2_subset, Cruze, tolerancia)
                lista_resultados.append(resultado_parcial)
        Todos = pd.concat(lista_resultados, ignore_index=True)
    
    tabla_cruzada=Todos[["Id_x","Id_y"]]
    Todo1=pd.merge(tabla_cruzada,data1,on="Id_x",how="left")
    Todo2=pd.merge(Todo1,data2,on="Id_y",how="left")
    return Todo2

# Función para obtener un resumen de las columnas de una tabla
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

# Función para encontrar elementos comunes entre dos listas
def Comunes(lista1, lista2, nombre="Key"):
    set1, set2 = set(lista1), set(lista2)
    todos_los_valores = set1 | set2
    reglas = ["OK" if valor in set1 and valor in set2 else "L1" if valor in set1 else "L2" for valor in todos_los_valores]
    
    return pd.DataFrame({nombre: list(todos_los_valores), "Regla": reglas})

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


def listar(lista):
    for x,y  in enumerate(lista):
        print(f"{x} {y}")