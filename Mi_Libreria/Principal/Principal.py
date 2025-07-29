import pandas as pd
import warnings
import numpy as np
import itertools
import re
from typing import List, Union, Optional, Dict, Any, Tuple

from pandas.api.types import (is_numeric_dtype, is_bool_dtype,
                              is_datetime64_any_dtype,is_string_dtype)


class DataProcessor:
    """Clase para procesar y manipular DataFrames"""
    
    @staticmethod
    def enumerar(lista: List[Any]) -> None:
        """
        Genera un listado numerado de los elementos de una lista
        """
        for x,y  in enumerate(lista):
            print(f"{x} {y}")

    @staticmethod
    def numeros(valor: Union[str, int, float]) -> Union[int, float, str]:
        """
        Convierte un valor a número entero o decimal, devuelve original si no es posible
        """
        original = str(valor).strip()
        try:
            return int(original)
        except ValueError:
            pass
        try:
            limpio = original.replace(".", "").replace(",", ".")
            return float(limpio)
        except ValueError:
            return original

    @staticmethod
    def extraer_numeros(texto: Any) -> List[Union[int, float]]:
        """
        Extrae todos los números de un texto y los devuelve como lista
        """
        texto = str(texto)  # Forzamos a string por si viene otro tipo (e.g., lista, int, float, etc.)
        numeros = re.findall(r'-?\d+(?:\.\d+)?', texto)
        return [int(n) if '.' not in n else float(n) for n in numeros]

    @staticmethod
    def valores_numericos(valor1: Any, operacion: Optional[callable] = None) -> Union[int, float, Any]:
        """
        Convierte un valor a numérico aplicando operación opcional
        """
        valor = str(valor1).strip()  # elimina espacios, tabs, saltos de línea al inicio y final
        if operacion is not None:
            valor = operacion(valor)
        try:
            return int(valor) 
        except ValueError:
            try:
                return float(valor)
                
            except ValueError:
                pass
                    
        return valor1

    @staticmethod
    def limpiar_valor(valor: Any) -> Union[str, float]:
        """
        Limpia texto numérico común eliminando símbolos de moneda y formato
        """
        if pd.isna(valor):
            return np.nan
        valor = str(valor).strip()

        # Reemplaza comunes: %, UF, $, CLP, etc.
        valor = re.sub(r"[^\d,.\-]", "", valor)

        # Reemplazo regional: si hay una coma pero no un punto, asume que la coma es decimal
        if valor.count(",") == 1 and valor.count(".") == 0:
            valor = valor.replace(",", ".")

        # Si hay miles con punto y decimales con coma: "1.234,56"
        if valor.count(",") == 1 and valor.count(".") >= 1 and valor.rfind(".") < valor.rfind(","):
            valor = valor.replace(".", "").replace(",", ".")

        return valor

    @staticmethod
    def convertir_valores(valor: Any) -> Union[bool, int, float, Any]:
        """
        Convierte strings a tipos apropiados: booleano, entero, decimal o mantiene original
        """
        if isinstance(valor, str):
            v = valor.strip().lower()
            if v in ["true", "verdadero", "sí", "si", "1"]:
                return True
            if v in ["false", "falso", "no", "0"]:
                return False

        try:
            return int(valor)
        except:
            try:
                return float(valor)
            except:
                return valor

    @staticmethod
    def convertir_columnas(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
        """
        Convierte automáticamente las columnas del DataFrame a sus tipos apropiados
        """
        df = df.copy()
        conversiones = { "fechas": [], "booleanas": [], "texto": [],"decimales": []}

        for col in df.columns:
            serie = df[col]

            # 4. Intentar fecha
            if serie.dtype == "object" or pd.api.types.is_datetime64_dtype(serie):
                fecha = pd.to_datetime(serie, errors="coerce", dayfirst=True)
                if fecha.notna().sum() >= len(serie.dropna()) * 0.9 and len(serie.dropna()) > 0:
                    df[col] = fecha
                    conversiones["fechas"].append(col)
                    continue

            # 1. Limpieza básica si es texto
            if serie.dtype == "object" or pd.api.types.is_string_dtype(serie):
                serie = serie.map(DataProcessor.limpiar_valor)

            # 2. Intentar booleano
            valores_unicos = set(str(x).strip().lower() for x in serie.dropna().unique())
            if valores_unicos.issubset({"true", "false", "sí", "si", "no", "verdadero", "falso", "1", "0"}):
                df[col] = serie.map(DataProcessor.convertir_valores)
                conversiones["booleanas"].append(col)
                continue

            # 3. Intentar numérico
            num = pd.to_numeric(serie, errors="coerce")
            if num.notna().sum() >= len(serie.dropna()) * 0.9 and len(serie.dropna()) > 0:
                es_entero = (num.dropna() % 1 == 0).all()
                if es_entero:
                    df[col] = num.astype("Int64")  # Soporta NaN en enteros
                    conversiones.setdefault("enteros", []).append(col)
                else:
                    df[col] = num
                    conversiones["decimales"].append(col)
                continue

            # 5. Dejar como texto
            df[col] = df[col].astype("string")
            conversiones["texto"].append(col)

        return df, conversiones

    @staticmethod
    def renombrar_columnas(df: pd.DataFrame) -> pd.DataFrame:
        """
        Convierte nombres de columnas a mayúsculas y reemplaza espacios y puntos por guiones bajos
        """
        columnas = df.columns
        columnas = [col.upper() for col in columnas]
        columnas = [col.replace(" ", "_").replace(".", "") for col in columnas]
        df.columns = columnas
        return df

    @staticmethod
    def comunes(lista1: List[Any], lista2: List[Any], nombre: str = "Key") -> pd.DataFrame:
        """
        Identifica elementos comunes y únicos entre dos listas
        """
        set1, set2 = set(lista1), set(lista2)
        todos_los_valores = set1 | set2
        reglas = ["OK" if valor in set1 and valor in set2 else "L1" if valor in set1 else "L2" for valor in todos_los_valores]
        
        return pd.DataFrame({nombre: list(todos_los_valores), "Regla": reglas})

    @staticmethod
    def resumen_columnas(tabla: pd.DataFrame) -> pd.DataFrame:
        """
        Genera resumen estadístico de cada columna del DataFrame
        """
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

    @staticmethod
    def añadir_key_and_indice(tabla: pd.DataFrame, columna: str = "Key", Key: bool = True, Indice: bool = False, excepciones: List[str] = []) -> pd.DataFrame:
        """
        Añade columna clave combinando valores de columnas y opcionalmente índice secuencial
        """
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

    @staticmethod
    def nuevo_registros(Tabla_nueva: pd.DataFrame, Tabla_antigua: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Identifica registros nuevos comparando dos DataFrames con misma estructura
        """
        col_nueva = Tabla_nueva.columns.values
        col_original = Tabla_antigua.columns.values

        if len(col_nueva) == len(col_original):
            tab_nueva = DataProcessor.añadir_key_and_indice(Tabla_nueva, Indice=True)
            tab_original = DataProcessor.añadir_key_and_indice(Tabla_antigua, Indice=True)
            
            l = DataProcessor.comunes(tab_nueva["Key2"], tab_original["Key2"]).rename(columns={"Key": "Key2"})
            new = l[l["Regla"] == "L1"].merge(tab_nueva, on="Key2", how="left")
            return new[col_nueva]
        else:
            print("Tablas distintas")
            return None

    @staticmethod
    def cruzar_registro(original: pd.DataFrame, nuevo: pd.DataFrame, excepciones: List[str] = [], method: str = "nuevos") -> pd.DataFrame:
        """
        Cruza registros entre DataFrames para encontrar nuevos o iguales
        """
        columna_original = original.columns
        columna_nuevo = nuevo.columns
        
        original = original.apply(lambda x: x.astype(int) if pd.api.types.is_float_dtype(x) and (x % 1 == 0).all() else x)
        nuevo = nuevo.apply(lambda x: x.astype(int) if pd.api.types.is_float_dtype(x) and (x % 1 == 0).all() else x)

        original = original.apply(lambda x: x.dt.strftime('%d-%m-%Y') if pd.api.types.is_datetime64_dtype(x) else x)
        nuevo = nuevo.apply(lambda x: x.dt.strftime('%d-%m-%Y') if pd.api.types.is_datetime64_dtype(x) else x)
        
        columns = DataProcessor.comunes(columna_original,columna_nuevo)
        excepciones = list(columns[columns["Regla"]!="OK"]["Key"].values)+excepciones
        columnas_final = columns[columns["Regla"]=="OK"]["Key"].values
        
        if len(original)>0:
            original_key = DataProcessor.añadir_key_and_indice(original,Indice=True,excepciones=excepciones)
            nuevo_key = DataProcessor.añadir_key_and_indice(nuevo,Indice=True,excepciones=excepciones)
            cruze = DataProcessor.comunes(original_key["Key2"],nuevo_key["Key2"])
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

    @staticmethod
    def rellenar_vacios(df: pd.DataFrame) -> pd.DataFrame:
        """
        Rellena valores vacíos del DataFrame según el tipo de dato de cada columna
        """
        df = df.copy()

        # Reemplaza strings vacíos explícitamente con NaN
        df.replace("", pd.NA, inplace=True)

        # Detecta tipos reales antes de rellenar
        df, _ = DataProcessor.convertir_columnas(df)

        for col in df.columns:
            serie = df[col]
            dtype = serie.dtype

            if is_numeric_dtype(dtype):
                df[col] = serie.fillna(0)

            elif is_bool_dtype(dtype):
                df[col] = serie.fillna(False)

            elif is_datetime64_any_dtype(dtype):
                df[col] = serie.fillna(pd.Timestamp("1900-01-01"))

            elif is_string_dtype(dtype) or dtype == object:
                df[col] = serie.fillna("")

            else:
                print(f"[!] Tipo no manejado: {col} ({dtype}) — sin modificar")

        return df

    @staticmethod
    def resumir(Tabla: pd.DataFrame, Agrup: str, Suma: Optional[str] = None) -> pd.DataFrame:
        """
        Genera resumen agrupado con conteos y opcionalmente sumas
        """
        if Suma:
            return Tabla.groupby([Agrup]).agg(can=(Agrup,"count"),suma=(Suma,"sum")).reset_index()
        else:
            return Tabla.groupby([Agrup]).agg(can=(Agrup,"count")).reset_index()

    @staticmethod
    def cruzar_diferencias(tab1: pd.DataFrame, tab2: pd.DataFrame) -> pd.DataFrame:
        """
        Compara diferencias estadísticas entre dos DataFrames en columnas comunes
        """
        ll = DataProcessor.comunes(tab1.columns,tab2.columns)
        OK = ll[ll["Regla"]=="OK"]
        L1 = ll[ll["Regla"]=="L1"]
        L2 = ll[ll["Regla"]=="L2"]
        
        ll = DataProcessor.resumen_columnas(tab1[OK["Key"]]).merge(DataProcessor.resumen_columnas(tab2[OK["Key"]]),on="Columna",how="outer")
        ll["Dif_Cantidad"] = ll["Cantidad_x"]-ll["Cantidad_y"]
        ll["Dif_Suma"] = ll["Suma_x"]-ll["Suma_y"]
        ll["Dif_Suma"] = ll["Suma_x"]-ll["Suma_y"]
        ll["Dif"] = ll["Dif_Cantidad"]+ll["Dif_Suma"]
        return ll


# Funciones de compatibilidad hacia atrás (mantienen nombres originales)
def Enumerar(lista: List[Any]) -> None:
    """Genera un listado numerado de los elementos de una lista"""
    return DataProcessor.enumerar(lista)

def Numeros(valor: Union[str, int, float]) -> Union[int, float, str]:
    """Convierte un valor a número entero o decimal, devuelve original si no es posible"""
    return DataProcessor.numeros(valor)

def Extraer_numeros(texto: Any) -> List[Union[int, float]]:
    """Extrae todos los números de un texto y los devuelve como lista"""
    return DataProcessor.extraer_numeros(texto)

def Valores_Numericos(valor1: Any, operacion: Optional[callable] = None) -> Union[int, float, Any]:
    """Convierte un valor a numérico aplicando operación opcional"""
    return DataProcessor.valores_numericos(valor1,operacion)

def convertir_columnas(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    """Convierte automáticamente las columnas del DataFrame a sus tipos apropiados"""
    return DataProcessor.convertir_columnas(df)

def Renombrar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte nombres de columnas a mayúsculas y reemplaza espacios y puntos por guiones bajos"""
    return DataProcessor.renombrar_columnas(df)

def Comunes(lista1: List[Any], lista2: List[Any], nombre: str = "Key") -> pd.DataFrame:
    """Identifica elementos comunes y únicos entre dos listas"""
    return DataProcessor.comunes(lista1, lista2, nombre)

def Resumen_columnas(tabla: pd.DataFrame) -> pd.DataFrame:
    """Genera resumen estadístico de cada columna del DataFrame"""
    return DataProcessor.resumen_columnas(tabla)

def Añadir_key_and_Indice(tabla: pd.DataFrame, columna: str = "Key", Key: bool = True, Indice: bool = False, excepciones: List[str] = []) -> pd.DataFrame:
    """Añade columna clave combinando valores de columnas y opcionalmente índice secuencial"""
    return DataProcessor.añadir_key_and_indice(tabla, columna, Key, Indice, excepciones)

def nuevo_registros(Tabla_nueva: pd.DataFrame, Tabla_antigua: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Identifica registros nuevos comparando dos DataFrames con misma estructura"""
    return DataProcessor.nuevo_registros(Tabla_nueva, Tabla_antigua)

def Cruzar_registro(original: pd.DataFrame, nuevo: pd.DataFrame, excepciones: List[str] = [], method: str = "nuevos") -> pd.DataFrame:
    """Cruza registros entre DataFrames para encontrar nuevos o iguales"""
    return DataProcessor.cruzar_registro(original,nuevo,excepciones,method)

def Rellenar_Vacios(df: pd.DataFrame) -> pd.DataFrame:
    """Rellena valores vacíos del DataFrame según el tipo de dato de cada columna"""
    return DataProcessor.rellenar_vacios(df)

def Resumir(Tabla: pd.DataFrame, Agrup: str, Suma: Optional[str] = None) -> pd.DataFrame:
    """Genera resumen agrupado con conteos y opcionalmente sumas"""
    return DataProcessor.resumir(Tabla,Agrup,Suma)

def Cruzar_Diferencias(tab1: pd.DataFrame, tab2: pd.DataFrame) -> pd.DataFrame:
    """Compara diferencias estadísticas entre dos DataFrames en columnas comunes"""
    return DataProcessor.cruzar_diferencias(tab1,tab2)
