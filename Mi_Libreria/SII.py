from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import re
import time 
import pandas as pd
import os

class Pagina():
    
    def __init__(self):
        
        self.Enlaces={
        "sii":"https://homer.sii.cl/",
        "RCV":"https://www4.sii.cl/consdcvinternetui/#/index",
        "Boletas1":"https://loa.sii.cl/cgi_IMT/TMBCOC_MenuConsultasContribRec.cgi?dummy=1461943244650",
        "Boletas2":"https://zeus.sii.cl/cvc_cgi/bte/bte_indiv_cons2",
        "F29":"https://www4.sii.cl/sifmConsultaInternet/index.html?dest=cifxx&form=29"
        }

        self.pagina=webdriver.Edge()
        self.pagina.get(self.Enlaces["sii"])
    
    def logn(self,rut,clave):
        tryi:
            InputRut=self.pagina.find_element(By.ID,"rutcntr")  
            InputClave = self.pagina.find_element(By.ID,"clave")
            Ingresar = self.pagina.find_element(By.ID,"bt_ingresar")
            
        except:
            assert False,"No se encontar los campos para ingresar al SII"

        InputRut.send_keys(rut)
        InputClave.send_keys(clave)
        Ingresar.click()

        respuesta = self.pagina.find_elements(By.ID,"alert_placeholder")
        assert len(respuesta)==0,"Rut Incorrecto"    
        respuesta = self.pagina.find_elements(By.ID,"titulo")
        assert len(respuesta)==0,"Contraseña Incorrecto"  

    def Exit(self):
        enlaces = self.pagina.find_elements(By.TAG_NAME,"a")
        for i in enlaces:
            if i.text == "Cerrar Sesión":
                salida = i
        salida.click()
    
    def Ingresar(self,pagina_sii=0):
        """(sii,RCV,RH)"""
        rutas=["sii","RCV","Boletas1","F29"]
        self.pagina.get(self.Enlaces[rutas[pagina_sii]])


def Datos(dato):
    try:
        return int(dato.replace(".",""))    
        
    except:
        return dato
    
def Relleno(lista,largo):
    if len(lista)>=largo:
        return lista[:largo]
        
    else:
        if len(lista)<largo:
            lista+=["" for x in range(largo-len(lista))]
            return lista
            
def Table(Tab):
    elementos=[]
    tamaño=[]
    for y in Tab.find_elements(By.TAG_NAME,"tr"):
        if y.text != " ":
            tr=[Datos(x.text) for x in y.find_elements(By.TAG_NAME,"td")]
            elementos.append(tr)
            tamaño.append(len(tr))
            
    Tab0=pd.DataFrame(columns=Relleno(elementos[0],max(tamaño)))
    for x in elementos:
        Tab0.loc[len(Tab0)]=Relleno(x,max(tamaño))

    Tab0.columns = ['Ver','N°','Estado','Fecha','Rut','Nombre o Razón Social','Soc. Prof.','Brutos','Retenido','Pagado','Boleta']
    Tab0 = Tab0[Tab0["Estado"].isin(["VIG","NULL"])]
    return Tab0   

def Buscar_Elenetos(elementos,nombre):
    for i in elementos:
        if nombre in i.text:
            return i
    return None

def Extraer_Numero(texto):
    return re.findall(r'-?\d+\.?\d*', texto)

class Procesos():
    def __init__(self,pagina):
        self.modulo=pagina
        self.pagina=self.modulo.pagina
        self.Ruta = "C:/Users/MaximilianoAlarcon/Downloads/"

    def Funcion_Espera_Boton(self,MsgError,buscador):
        try:
            # Esperar a que el botón de ingreso sea visible
            btn = WebDriverWait(self.pagina, 2).until(
                EC.visibility_of_element_located(buscador)
            ) 
            btn.click()  # Hacer clic en el botón
            
        except TimeoutException:
            print(MsgError)
            
        except Exception as e:
            print(f"Otro error ocurrió: {e}")
        
    def Extraer_Tabla(self):

        table = self.pagina.find_element(By.CLASS_NAME,"ng-scope")
        Registros = len(table.find_elements(By.TAG_NAME,"tr"))-1
        
        Tabla_Final =[]
        
        for x in range(Registros):
            table = self.pagina.find_element(By.CLASS_NAME,"ng-scope")
            fila = table.find_elements(By.TAG_NAME,"tr")[x+1]
            Extra = fila.find_element(By.TAG_NAME,"a")
            Extra_Extra = Extra.text
            Extra.click()
            time.sleep(2)
            try:
                cantidad = self.pagina.find_element(By.NAME,"tableCompra_length")
                cantidad.send_keys(100)
            
                Registro = self.pagina.find_element(By.ID,"tableCompra")
                html = Registro.get_attribute("outerHTML")
                registro = pd.read_html(html)[0]
                registro["Extra"]=Extra_Extra
                Tabla_Final.append(registro)
            except:
                for y in self.pagina.find_elements(By.TAG_NAME,"button"):
                    if y.text == "Cerrar":
                        y.click()
                        break
            time.sleep(2)
            for y in self.pagina.find_elements(By.TAG_NAME,"button"):
                if y.text == "Volver":
                    y.click()
                    break
            time.sleep(1)
            for x in self.pagina.find_elements(By.TAG_NAME,"a"):
                if x.text == "Pendientes":
                    x.click()
                    break
        try:
            Registro_Final = pd.concat(Tabla_Final)
            Registro_Final[Registro_Final[Registro_Final.columns[1]]!=Registro_Final.columns[1]]
            return [Registro_Final,"Descarga Registro de Compra"]
        
        except:
            return [pd.DataFrame(),"Sin Registro de Compra"]

    def Extraer_Compra(self,Tipo=False):
        table = self.pagina.find_element(By.CLASS_NAME,"ng-scope")
        Registros = len(table.find_elements(By.TAG_NAME,"tr"))-1
        
        Tabla_Final =[]
        val = False
        
        for x in range(Registros):
    
            if Tipo:
                for u in self.pagina.find_elements(By.TAG_NAME,"a"):
                    if u.text == "Pendientes":
                        val = True
                        u.click()
                        break
    
                assert val, "Error"
    
            time.sleep(1)
            table = self.pagina.find_element(By.CLASS_NAME,"ng-scope")
            fila = table.find_elements(By.TAG_NAME,"tr")[x+1]
            
            Extra = fila.find_element(By.TAG_NAME,"a")
            Extra_Extra = Extra.text
            Extra.click()
            time.sleep(2)
            
            try:
                cantidad = self.pagina.find_element(By.NAME,"tableCompra_length")
                cantidad.send_keys(100)
                Registro = self.pagina.find_element(By.ID,"tableCompra")
                html = Registro.get_attribute("outerHTML")
                registro = pd.read_html(html)[0]
                registro["Extra"]=Extra_Extra
                Tabla_Final.append(registro)
                
            except:
                for y in self.pagina.find_elements(By.TAG_NAME,"button"):
                    if y.text == "Cerrar":
                        y.click()
                        break
                        
            time.sleep(2)
            for y in self.pagina.find_elements(By.TAG_NAME,"button"):
                if y.text == "Volver":
                    y.click()
                    break
        
            time.sleep(1)
        print("Proceso")
        Registro_Final = pd.concat(Tabla_Final)
        Registro_Final = Registro_Final[Registro_Final[Registro_Final.columns[1]]!=Registro_Final.columns[1]]
        Registro_Final = Registro_Final.applymap(lambda x: Datos(x))
        Registro_Final["Cod"]=[Extraer_Numero(x)[0] for x in Registro_Final["Extra"]]
        return Registro_Final
    
    def Compra_Venta(self,mes,ano,Compra=True,Venta=False,Rut="",Empresa1=""):
            Reporte={}
            Empresa = self.pagina.find_elements(By.NAME,"rut")
            Periodo=self.pagina.find_elements(By.ID,"periodoMes")
            Ano=self.pagina.find_elements(By.TAG_NAME,"select") 
            for zzz in Ano:
                if zzz.text[:3]=="Año":
                    Ano0=zzz
        
            assert len(Empresa)>0,"Campos No encontrados"
            Periodo[0].send_keys(mes)
            if ano!=None:
                Ano0.send_keys(str(ano))

            time.sleep(1)
            botones = self.pagina.find_elements(By.CLASS_NAME,"btn")  
            boton=Buscar_Elenetos(botones,"Consultar")
            boton.click()
            time.sleep(3)
        
            #Compras
            if True:
                RC = pd.DataFrame()
                RC= self.Extraer_Compra()

                # except:
                #     pass
            
                # try:
                RC1 = pd.DataFrame()
                RC1 = self.Extraer_Compra(Tipo=True)
                # except:
                #     pass

                with pd.ExcelWriter(f"C:/Users/MaximilianoAlarcon/Downloads/{Empresa1}_{mes}.xlsx",engine='openpyxl') as write:
                    RC.to_excel(write, sheet_name='Hoja1',index=False)
                    RC1.to_excel(write, sheet_name='Hoja2',index=False)
        
            #Ventas
            if Venta:
                botones = self.pagina.find_elements(By.CLASS_NAME,"a")  
                btn_venta=Buscar_Elenetos(botones,"VENTA")
                assert btn_venta != None ,"Bonton pendiente no encontrado"
                btn_venta.click()
             
            return Reporte

    def Registro_Compra(self,meses,ano=None,Empresa1="RC"):
        self.modulo.Ingresar(pagina_sii=1)
        assert type(meses)==list,"Los meses deben estar en una lista"
        for mes in meses:
            Reporte=self.Compra_Venta(Empresa1,mes,ano)


#----------------------------------------------------------------------------------------------
            
    def Boleta(self, mes, ano=None, inicial=True):
        Reporte={}
        if inicial:
            if ano != None :
                self.pagina.find_elements(By.NAME,"cbanoinformeanual").Select(ano)
            self.Funcion_Espera_Boton("No se pudo ingresar al registro",(By.ID, "cmdconsultar124"))
        
        try:
            
            time.sleep(1)
            enlaces = self.pagina.find_elements(By.TAG_NAME,"a")
            i=Buscar_Elenetos(enlaces,mes)
            i.click()

        
        except:
            return None
            # assert False,"No se pudo ingresar al mes"
            
        try:
            time.sleep(2)
            Tablas = self.pagina.find_elements(By.TAG_NAME,"table")
            
            Tab=Buscar_Elenetos(Tablas,"Soc. Prof.")
            assert Tab!=None, "No se encontro Tabla" 
            
            return Table(Tab)
        
        except Exception as e:
            assert False, e

    
    def Registro_Honorario(self,meses,ano=None,Nombre=None):
        self.modulo.Ingresar(pagina_sii=2)
        assert type(meses)==list,"Los meses deben estar en una lista"
        for indice, mes in enumerate(meses):
            inicial = (indice==0)
            Reporte=self.Boleta(mes,ano,inicial)
            if Reporte is not None:
                if Nombre is None:
                    Reporte.to_excel(f"C:/Users/MaximilianoAlarcon/Downloads/{mes}.xlsx",index=False)
                else:
                    Reporte.to_excel(f"C:/Users/MaximilianoAlarcon/Downloads/{Nombre}_{mes}.xlsx",index=False)
            self.pagina.back()
            
    
    def F29(self,meses,detalle = False):
        self.modulo.Ingresar(pagina_sii=3)
        assert type(meses)==list,"Los meses deben estar en una lista"

        for indice, mes in enumerate(meses):
            time.sleep(3)
            recuadro = self.pagina.find_element(By.ID,"frame-window")
            for x in recuadro.find_elements(By.TAG_NAME,"a"):
                if "F29" in x.text:
                    btn = x
            btn.click()
            time.sleep(2)

            recuadro = self.pagina.find_element(By.ID,"frame-window")
            Tabla=recuadro.find_element(By.CLASS_NAME,"gw-tabla-integral_boostrap")
            
            Tabla_1 = pd.read_html(Tabla.get_attribute("outerHTML"))[0]
            F29=Tabla_1[~pd.isna(Tabla_1[0])]
            F29.columns = ["Meses"]+[f"{2024-x}" for x in range(F29.shape[1]-1)]
            F29 = F29[F29["Meses"]!="F29 (-)"]

            fila = list(F29["Meses"].values).index(mes.title())
            Estado = F29.iloc[fila,1]

            if Estado =='Declaración sin observaciones.':

                Tabla=recuadro.find_element(By.CLASS_NAME,"gw-tabla-integral_boostrap")
                enlaces = Tabla.find_elements(By.TAG_NAME,"img")
                
                filas = Tabla.find_element(By.TAG_NAME,"table").find_element(By.TAG_NAME,"tbody").find_elements(By.XPATH,"./tr",)
                
                for y,x in enumerate(filas):
                    if mes.upper() in x.text.upper():
                        x.find_elements(By.TAG_NAME,"td")[1].click()
                        break
                        
                time.sleep(2)
                for x in self.pagina.find_elements(By.TAG_NAME,"button"):
                    if x.text =="Formulario Compacto":
                        btn = x
                        break
                btn .click()

                self.pagina.switch_to.window(self.pagina.window_handles[1])
                self.pagina.maximize_window()
                time.sleep(2)
                self.pagina.save_screenshot(f"C:/Users/MaximilianoAlarcon/Downloads/F29 {mes}.png")
                self.pagina.close()
                self.pagina.switch_to.window(self.pagina.window_handles[0])

                for x in self.pagina.find_elements(By.TAG_NAME,"button"):
                    if x.text == "Volver":
                        btn = x
                        break
                btn.click()

            
            else :
                pass