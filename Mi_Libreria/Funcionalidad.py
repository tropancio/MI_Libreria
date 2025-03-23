import pandas as pd
import ipywidgets as widgets
from IPython.display import display
from ipydatagrid import DataGrid
from io import BytesIO
from IPython import get_ipython

def Cargar_excel(nombre_variable='df'):
    global df
    uploader = widgets.FileUpload(accept='.csv, .xlsx', multiple=False)
    boton_cargar = widgets.Button(description="Cargar archivo", button_style='success')
    output = widgets.Output()
    hoja_dropdown = widgets.Dropdown(description='Hoja:', options=[], layout=widgets.Layout(width='50%'))
    hoja_dropdown.layout.display = 'none'  # Oculto por defecto

    estado = {
        'contenido': None,
        'nombre_archivo': None,
        'tipo_archivo': None,
        'hoja_seleccionada': None
    }

    def procesar_archivo():
        if not uploader.value:
            return False

        archivo = uploader.value[0]  # ✅ CORREGIDO
        estado['contenido'] = archivo['content']
        estado['nombre_archivo'] = archivo.get('name') or archivo.get('metadata', {}).get('name')

        if estado['nombre_archivo'].endswith('.csv'):
            estado['tipo_archivo'] = 'csv'
            hoja_dropdown.layout.display = 'none'
            return True

        elif estado['nombre_archivo'].endswith('.xlsx'):
            estado['tipo_archivo'] = 'xlsx'
            try:
                excel_file = pd.ExcelFile(BytesIO(estado['contenido']))
                hoja_dropdown.options = excel_file.sheet_names
                hoja_dropdown.layout.display = 'flex'
                estado['hoja_seleccionada'] = hoja_dropdown.options[0]
                return True
            except Exception as e:
                with output:
                    output.clear_output()
                    print(f"❌ Error al leer hojas del Excel: {e}")
                return False

        return False

    def on_file_upload(change):
        if procesar_archivo():
            with output:
                output.clear_output()
                print(f"📄 Archivo seleccionado: {estado['nombre_archivo']}")
                if estado['tipo_archivo'] == 'xlsx':
                    print("📑 Seleccioná una hoja para cargar.")
        else:
            with output:
                output.clear_output()
                print("⚠️ No se pudo procesar el archivo.")

    def on_dropdown_change(change):
        if change['type'] == 'change' and change['name'] == 'value':
            estado['hoja_seleccionada'] = change['new']

    def on_button_click(b):
        with output:
            output.clear_output()

            if not estado['contenido']:
                if not procesar_archivo():
                    print("⚠️ Primero subí un archivo válido.")
                    return

            try:
                if estado['tipo_archivo'] == 'csv':
                    df = pd.read_csv(BytesIO(estado['contenido']))
                elif estado['tipo_archivo'] == 'xlsx':
                    if not estado['hoja_seleccionada']:
                        print("⚠️ Seleccioná una hoja.")
                        return
                    df = pd.read_excel(BytesIO(estado['contenido']), sheet_name=estado['hoja_seleccionada'])
                else:
                    print("❌ Formato no soportado.")
                    return

                # Inyectar variable al entorno del notebook
                get_ipython().user_ns[nombre_variable] = df
                print(f"✅ Archivo cargado como `{nombre_variable}`.")
                if estado['tipo_archivo'] == 'xlsx':
                    print(f"📑 Hoja seleccionada: {estado['hoja_seleccionada']}")
                print(df.head())

            except Exception as e:
                print(f"❌ Error al procesar el archivo: {e}")

    uploader.observe(on_file_upload, names='value')
    hoja_dropdown.observe(on_dropdown_change, names='value')
    boton_cargar.on_click(on_button_click)

    display(widgets.VBox([uploader, hoja_dropdown, boton_cargar, output]))

def tabla():
    return df

def display_tabla(df):
    dg = DataGrid(df)
    display(dg)