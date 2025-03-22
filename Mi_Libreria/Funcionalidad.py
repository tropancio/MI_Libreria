import pandas as pd
import ipywidgets as widgets
from IPython.display import display

from ipydatagrid import DataGrid

def Cargar_excel(nombre_variable='df'):
    uploader = widgets.FileUpload(
        accept='.csv, .xlsx',
        multiple=False
    )

    def on_upload_change(change):
        uploaded_file = list(uploader.value.values())[0]
        content = uploaded_file['content']
        name = uploaded_file['metadata']['name']

        if name.endswith('.csv'):
            df = pd.read_csv(pd.io.common.BytesIO(content))
        elif name.endswith('.xlsx'):
            df = pd.read_excel(pd.io.common.BytesIO(content))
        else:
            print("Formato no soportado")
            return

        # Guardar como variable global con el nombre que elijas
        globals()[nombre_variable] = df
    uploader.observe(on_upload_change, names='value')
    display(uploader)

def display_tabla(df):
    dg = DataGrid(df)
    display(dg)
