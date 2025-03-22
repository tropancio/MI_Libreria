import pandas as pd
import numpy as np
import itertools


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
