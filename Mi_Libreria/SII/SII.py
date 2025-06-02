from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import time 
import pandas as pd
import warnings
import os

from Mi_Libreria.Principal.Principal import *

class Pagina():
    
    def __init__(self):
        
        self.Enlaces={
        "sii":"https://homer.sii.cl/",
        "RCV":"https://www4.sii.cl/consdcvinternetui/#/index",
        "Boletas1":"https://loa.sii.cl/cgi_IMT/TMBCOC_MenuConsultasContribRec.cgi?dummy=1461943244650",
        "Boletas2":"https://zeus.sii.cl/cvc_cgi/bte/bte_indiv_cons2",
        "F29":"https://www4.sii.cl/sifmConsultaInternet/index.html?dest=cifxx&form=29",
        "DJ_Declarada1":"https://www2.sii.cl/djconsulta/estadoddjjs",
        "DJ_Declarada2":"https://www4.sii.cl/djconsultarentaui/internet/#/consulta/",
        "DJ_Agente_retenedor":"https://www4.sii.cl/djconsultarentaui/internet/#/agenteretenedor/",
        "layout":"https://alerce.sii.cl/dior/dej/html/dj_autoverificacion.html"
        }

        self.pagina=webdriver.Edge()
        self.pagina.get(self.Enlaces["sii"])
    
    def Login(self,credenciales):
        """
        credenciales = [rut ,clave]
        """
        rut,clave = credenciales
        try:
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
        salida = WebDriverWait(self.pagina, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//*[text()="Cerrar Sesión"]'))
            )
        salida.click()
    
    def Ingresar(self,pagina_sii=0):
        """
        pagina_sii:
            0 sii
            1 RCV
            2 Boletas1
            3 Boletas2
            4 F29
            5 DJ_Declarada1
            6 DJ_Declarada2
            7 DJ_Agente_retenedor
        """
        rutas = [x for x in self.Enlaces.keys()]
        self.pagina.get(self.Enlaces[rutas[pagina_sii]])


class Procesos():
    def __init__(self,pagina):
        self.modulo=pagina
        self.pagina=self.modulo.pagina
        # self.Ruta = "C:/Users/MaximilianoAlarcon/Downloads/"

    def formatear_texto(self,texto):
        return texto.upper().replace(" ", "_")

    def Ingresar_Periodo_RCV(self,Periodo=[]):
        """
        Ingresa un Periodo al formulario de Registro de compra
        Periodo = [mes,año]
        """
        Contenedor = WebDriverWait(self.pagina, 10).until(
            EC.presence_of_element_located((By.NAME, "formContribuyente"))
        )
        if len(Periodo)>0:
            mes,ano = Periodo
            meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
            Rut = WebDriverWait(Contenedor, 10).until(
                EC.presence_of_element_located((By.NAME, "rut"))
            )
            Periodo = WebDriverWait(Contenedor, 10).until(
                EC.presence_of_element_located((By.ID, "periodoMes"))
            )
            Periodo.send_keys(meses[mes])
            Año = WebDriverWait(Contenedor, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@ng-model="periodoAnho"]'))
            )
            Año.send_keys(str(ano))   
        boton = WebDriverWait(Contenedor, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME,"btn"))
        )
        boton.click()
        
    def Consultar_Existencia_Registros(self):
        """
        En la pestaña de RCV revisa que haya reigstros para consultar, devuelve
        Registors -> True
        Sin Reigstros -> False
        """
        try:
            time.sleep(1)
            WebDriverWait(self.pagina,1).until(
                EC.presence_of_element_located((By.CLASS_NAME,"alert-danger"))
            )          
            return False
            
        except:
            return True
            
    def Ingresar_registro_RV(self,registro=0):
        """
        Ingresa a los diferentes tipos de registro
        0 COMPRA
        1 VENTA
        2 Pendiente
        """
    
        if registro == 0 or registro == 2:
    
            compra = WebDriverWait(self.pagina, 10).until(
                EC.presence_of_element_located((By.ID,'tabCompra'))
            )
            
            compra.click()  
            
            if registro == 0:
                return None
    
            pendiente = WebDriverWait(self.pagina, 10).until(
                EC.presence_of_element_located((By.XPATH, f'//*[text()="Pendientes"]'))
                )
            
            pendiente.click()
            return None
            
        elif registro == 1:
            
            ventas = WebDriverWait(self.pagina, 10).until(
                EC.presence_of_element_located((By.XPATH, f'//*[text()="VENTA"]'))
                )
            
            ventas.click()
            return None
        
    def Extraer_Registro(self,tipo1 = 0):
        """
        0 Compra
        1 Ventas
        """
        
        tipo0 = {
            "Compra" : ["tableCompra_length","tableCompra_paginate"],
            "Ventas" : ["tableVenta_length","tableVenta_wrapper"]
        }
        
        tipo2 = [x for x in tipo0]
        
        Contenedor_tabla = WebDriverWait(self.pagina, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ng-scope"))
        )
        tabla_resumen = WebDriverWait(Contenedor_tabla, 10).until(
            EC.presence_of_element_located((By.TAG_NAME,"table"))
        )
    
        
        a = pd.read_html(tabla_resumen.get_attribute("outerHTML"))[0]
        
        resumen = a.copy()
        resumen = convertir_columnas(resumen.fillna(0))
        resumen["TIPO"] = [Extraer_numeros(x)[0] for x in resumen["Tipo Documento"]]
        
        a = a.rename(columns = {x : self.formatear_texto(x) for x in a.columns})
        a = a[a["TOTAL_DOCUMENTOS"]>0]
        
    
        Todas_las_tablas = []
        
        for tipo_registro in a["TIPO_DOCUMENTO"]:
            try:
                tipo = WebDriverWait(Contenedor_tabla, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[text()="{tipo_registro}"]'))
                    )
                tipo.click()
                
                detalle = WebDriverWait(self.pagina, 10).until(
                    EC.presence_of_element_located((By.ID, 'detalle'))
                    )
        
                largo_tabla = WebDriverWait(self.pagina, 10).until(
                    EC.presence_of_element_located((By.ID, tipo0[tipo2[tipo1]][0]))
                    )
                
                tabla_detalle = WebDriverWait(detalle, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'table'))
                    )
                
                nav_pagina = WebDriverWait(self.pagina, 10).until(
                    EC.presence_of_element_located((By.ID, tipo0[tipo2[tipo1]][1]))
                    )
                                
                tabla = WebDriverWait(detalle, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'table'))
                    )   
                
                registros = pd.read_html(detalle.get_attribute("outerHTML"))
            
                for x1 in registros:
                    if len(x1)>1:
                        registro = x1
        
                registro["TIPO"] = Extraer_numeros(tipo_registro)[0]
            
                Volver = WebDriverWait(self.pagina, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//*[text()="Volver"]'))
                    )
                Volver.click()
            
                Todas_las_tablas.append(registro)
                
            except:
                pass
    
        final_final = pd.concat(Todas_las_tablas)
        final_final = final_final.rename(columns={x:self.formatear_texto(x) for x in final_final.columns})
        final_final = final_final[final_final["TIPO_COMPRA"]=="Del Giro"]
        final_final = convertir_columnas(final_final.fillna(0))
        
        return [resumen,final_final]
    
    def Compra_Venta(self, Parametro=[],Rut="",Empresa1=""):
            self.modulo.Ingresar(pagina_sii=1)
            self.Ingresar_Periodo_RCV(Parametro)
        
            #Compras
            RC = pd.DataFrame()
    
            self.Ingresar_registro_RV(registro=0)
            if self.Consultar_Existencia_Registros():
                    resumen,rc = self.Extraer_Registro(tipo1=0)
                    RC = rc
        
            #Pendiente
            RCP = pd.DataFrame()
        
            self.Ingresar_registro_RV(registro=2)
            if self.Consultar_Existencia_Registros():
                    resumen,rc = self.Extraer_Registro(tipo1=0)
                    RCP = rc
    
            #Ventas
            RV = pd.DataFrame()
    
            self.Ingresar_registro_RV(registro=1)
            if self.Consultar_Existencia_Registros():
                    resumen,rc = self.Extraer_Registro(tipo1=1)
                    RV = rc
        
            Reporte={
                "RC" : RC, "RCP" : RCP, "RV" : RV   
            } 
    
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