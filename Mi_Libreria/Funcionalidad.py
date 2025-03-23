import pandas as pd
import ipywidgets as widgets
from IPython.display import display
from ipydatagrid import DataGrid

def Cargar_excel(nombre_variable='df'):
    uploader = widgets.FileUpload(
        accept='.csv, .xlsx',
        multiple=False
    )

    output = widgets.Output()

    def on_upload_change(change):
        if not uploader.value:
            with output:
                output.clear_output()
                print("No se subió ningún archivo.")
            return

        try:
            uploaded_file = uploader.value[0]
            content = uploaded_file['content']
            # Soporte para diferentes versiones de ipywidgets
            name = uploaded_file.get('name') or uploaded_file.get('metadata', {}).get('name')

            if not name:
                raise ValueError("No se pudo obtener el nombre del archivo.")

            if name.endswith('.csv'):
                df = pd.read_csv(BytesIO(content))
            elif name.endswith('.xlsx'):
                df = pd.read_excel(BytesIO(content))
            else:
                with output:
                    output.clear_output()
                    print("Formato no soportado.")
                return

            globals()[nombre_variable] = df

            with output:
                output.clear_output()
                print(f"✅ Archivo cargado como variable global: `{nombre_variable}`")

        except Exception as e:
            with output:
                output.clear_output()
                print(f"❌ Error al leer el archivo: {e}")

    uploader.observe(on_upload_change, names='value')
    display(uploader, output)



def display_tabla(df):
    dg = DataGrid(df)
    display(dg)