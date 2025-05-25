"""
Módulo SII con Playwright para automatización web del Servicio de Impuestos Internos de Chile.

Este módulo proporciona una alternativa moderna a Selenium usando Playwright para realizar
web scraping y automatización de tareas en el sitio web del SII.

Ventajas de Playwright sobre Selenium:
- Más rápido y estable
- Mejor manejo de contenido dinámico
- Capturas de pantalla automáticas en caso de error
- Soporte nativo para múltiples navegadores
- Mejor manejo de timeouts y esperas
"""

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from playwright.sync_api import sync_playwright, Page as SyncPage, Browser as SyncBrowser
import asyncio
import pandas as pd
import logging
from typing import Optional, Dict, List, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
import os
from datetime import datetime
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConfiguracionSII:
    """Configuración para la automatización del SII con Playwright."""
    
    # Timeouts
    timeout_navegacion: int = 30000  # 30 segundos
    timeout_elemento: int = 10000    # 10 segundos
    
    # Configuración del navegador
    headless: bool = False
    navegador: str = "chromium"  # chromium, firefox, webkit
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    
    # Directorios
    directorio_descargas: Path = field(default_factory=lambda: Path.home() / "Downloads" / "SII")
    directorio_capturas: Path = field(default_factory=lambda: Path.home() / "Downloads" / "SII" / "capturas")
    
    # URLs del SII
    urls: Dict[str, str] = field(default_factory=lambda: {
        "sii": "https://homer.sii.cl/",
        "rcv": "https://www4.sii.cl/consdcvinternetui/#/index",
        "boletas_honorarios": "https://loa.sii.cl/cgi_IMT/TMBCOC_MenuConsultasContribRec.cgi",
        "boletas_consulta": "https://zeus.sii.cl/cvc_cgi/bte/bte_indiv_cons2",
        "f29": "https://www4.sii.cl/sifmConsultaInternet/index.html?dest=cifxx&form=29",
        "dj_declarada": "https://www2.sii.cl/djconsulta/estadoddjjs",
        "dj_renta": "https://www4.sii.cl/djconsultarentaui/internet/#/consulta/",
        "agente_retenedor": "https://www4.sii.cl/djconsultarentaui/internet/#/agenteretenedor/",
        "layout": "https://alerce.sii.cl/dior/dej/html/dj_autoverificacion.html"
    })
    
    def __post_init__(self):
        """Crear directorios si no existen."""
        self.directorio_descargas.mkdir(parents=True, exist_ok=True)
        self.directorio_capturas.mkdir(parents=True, exist_ok=True)


@dataclass
class CredencialesSII:
    """Maneja las credenciales del SII de forma segura."""
    
    rut: str
    clave: str
    
    @classmethod
    def desde_variables_entorno(cls) -> 'CredencialesSII':
        """Carga credenciales desde variables de entorno."""
        rut = os.getenv('SII_RUT')
        clave = os.getenv('SII_CLAVE')
        
        if not rut or not clave:
            raise ValueError(
                "Credenciales SII no encontradas. "
                "Define las variables de entorno SII_RUT y SII_CLAVE"
            )
        
        return cls(rut=rut, clave=clave)
    
    def __repr__(self) -> str:
        """Representación segura sin mostrar la clave."""
        return f"CredencialesSII(rut='{self.rut}', clave='***')"


class SesionSIIPlaywright:
    """Maneja la sesión web del SII usando Playwright."""
    
    def __init__(self, config: Optional[ConfiguracionSII] = None):
        self.config = config or ConfiguracionSII()
        self.playwright = None
        self.navegador: Optional[SyncBrowser] = None
        self.contexto: Optional[BrowserContext] = None
        self.pagina: Optional[SyncPage] = None
        self._sesion_iniciada = False
    
    def __enter__(self) -> 'SesionSIIPlaywright':
        """Context manager para manejo automático de recursos."""
        self.inicializar_navegador()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Limpieza automática de recursos."""
        self.cerrar()
    
    def inicializar_navegador(self):
        """Inicializa el navegador Playwright."""
        try:
            self.playwright = sync_playwright().start()
            
            # Seleccionar navegador
            if self.config.navegador == "firefox":
                self.navegador = self.playwright.firefox.launch(headless=self.config.headless)
            elif self.config.navegador == "webkit":
                self.navegador = self.playwright.webkit.launch(headless=self.config.headless)
            else:
                self.navegador = self.playwright.chromium.launch(headless=self.config.headless)
            
            # Crear contexto con configuración de descarga
            self.contexto = self.navegador.new_context(
                viewport=self.config.viewport,
                accept_downloads=True,
            )
            
            # Configurar timeouts
            self.contexto.set_default_timeout(self.config.timeout_elemento)
            self.contexto.set_default_navigation_timeout(self.config.timeout_navegacion)
            
            # Crear página
            self.pagina = self.contexto.new_page()
            
            logger.info(f"Navegador {self.config.navegador} inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando navegador: {e}")
            self.cerrar()
            raise
    
    def iniciar_sesion(self, credenciales: CredencialesSII) -> bool:
        """
        Inicia sesión en el SII.
        
        Args:
            credenciales: Credenciales del SII
            
        Returns:
            True si el login fue exitoso, False en caso contrario
            
        Raises:
            Exception: Si hay errores en el proceso de login
        """
        try:
            logger.info("Iniciando sesión en el SII...")
            
            # Navegar a la página principal
            self.pagina.goto(self.config.urls["sii"])
            
            # Esperar y llenar el formulario de login
            self.pagina.wait_for_selector("#rutcntr", timeout=self.config.timeout_elemento)
            self.pagina.fill("#rutcntr", credenciales.rut)
            self.pagina.fill("#clave", credenciales.clave)
            
            # Hacer clic en ingresar
            self.pagina.click("#bt_ingresar")
            
            # Verificar login exitoso
            self._verificar_login_exitoso()
            
            self._sesion_iniciada = True
            logger.info("Sesión iniciada correctamente")
            return True
            
        except Exception as e:
            # Capturar pantalla en caso de error
            self._capturar_pantalla_error("error_login")
            logger.error(f"Error en login: {e}")
            raise
    
    def _verificar_login_exitoso(self):
        """Verifica que el login haya sido exitoso."""
        try:
            # Esperar un poco para que cargue la respuesta
            self.pagina.wait_for_timeout(2000)
            
            # Verificar si hay errores de RUT
            if self.pagina.locator("#alert_placeholder").count() > 0:
                raise Exception("RUT incorrecto o no válido")
            
            # Verificar si hay errores de contraseña
            if self.pagina.locator("#titulo").count() > 0:
                raise Exception("Contraseña incorrecta")
            
            # Verificar que hayamos llegado a la página principal (opcional)
            # Esto puede variar según la estructura actual del SII
            
        except Exception as e:
            if "RUT incorrecto" in str(e) or "Contraseña incorrecta" in str(e):
                raise
            else:
                logger.warning(f"No se pudo verificar completamente el login: {e}")
    
    def navegar_a_seccion(self, seccion: str):
        """
        Navega a una sección específica del SII.
        
        Args:
            seccion: Nombre de la sección (clave del diccionario urls)
        """
        if not self._sesion_iniciada:
            raise Exception("Debe iniciar sesión antes de navegar")
        
        if seccion not in self.config.urls:
            raise ValueError(f"Sección '{seccion}' no encontrada. Secciones disponibles: {list(self.config.urls.keys())}")
        
        url = self.config.urls[seccion]
        logger.info(f"Navegando a {seccion}: {url}")
        
        self.pagina.goto(url)
        self.pagina.wait_for_load_state("networkidle")
    
    def cerrar_sesion(self):
        """Cierra la sesión actual del SII."""
        if self._sesion_iniciada:
            try:
                # Buscar el enlace de cerrar sesión
                cerrar_sesion_selector = 'text="Cerrar Sesión"'
                if self.pagina.locator(cerrar_sesion_selector).count() > 0:
                    self.pagina.click(cerrar_sesion_selector)
                    logger.info("Sesión cerrada correctamente")
                else:
                    logger.warning("No se encontró el enlace para cerrar sesión")
            except Exception as e:
                logger.error(f"Error al cerrar sesión: {e}")
            finally:
                self._sesion_iniciada = False
    
    def _capturar_pantalla_error(self, nombre: str):
        """Captura pantalla en caso de error."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = self.config.directorio_capturas / f"{nombre}_{timestamp}.png"
            self.pagina.screenshot(path=str(archivo))
            logger.info(f"Captura de pantalla guardada: {archivo}")
        except Exception as e:
            logger.error(f"Error capturando pantalla: {e}")
    
    def cerrar(self):
        """Cierra todos los recursos del navegador."""
        try:
            if self._sesion_iniciada:
                self.cerrar_sesion()
            
            if self.pagina:
                self.pagina.close()
            
            if self.contexto:
                self.contexto.close()
            
            if self.navegador:
                self.navegador.close()
            
            if self.playwright:
                self.playwright.stop()
            
            logger.info("Recursos del navegador cerrados correctamente")
            
        except Exception as e:
            logger.error(f"Error cerrando recursos: {e}")


class ExtractorRCV:
    """Extractor de datos de Registro de Compras y Ventas."""
    
    def __init__(self, sesion: SesionSIIPlaywright):
        self.sesion = sesion
        self.pagina = sesion.pagina
    
    def extraer_registro_periodo(self, mes: int, año: int) -> Dict[str, pd.DataFrame]:
        """
        Extrae los registros de compra y venta para un período específico.
        
        Args:
            mes: Mes (1-12)
            año: Año (ej: 2024)
            
        Returns:
            Diccionario con DataFrames de compras, ventas y pendientes
        """
        logger.info(f"Extrayendo registros para {mes:02d}/{año}")
        
        # Navegar a RCV
        self.sesion.navegar_a_seccion("rcv")
        
        # Ingresar período
        self._ingresar_periodo(mes, año)
        
        # Extraer datos
        resultado = {
            "compras": self._extraer_compras(),
            "ventas": self._extraer_ventas(),
            "pendientes": self._extraer_pendientes()
        }
        
        return resultado
    
    def _ingresar_periodo(self, mes: int, año: int):
        """Ingresa el período en el formulario."""
        try:
            # Esperar el formulario
            self.pagina.wait_for_selector('form[name="formContribuyente"]')
            
            # Seleccionar mes
            meses = [
                'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
            ]
            
            mes_selector = "#periodoMes"
            self.pagina.select_option(mes_selector, meses[mes - 1])
            
            # Ingresar año
            año_selector = '[ng-model="periodoAnho"]'
            self.pagina.fill(año_selector, str(año))
            
            # Hacer clic en consultar
            self.pagina.click("button.btn")
            
            # Esperar a que cargue
            self.pagina.wait_for_load_state("networkidle")
            
        except Exception as e:
            self._capturar_error("error_periodo")
            raise Exception(f"Error ingresando período: {e}")
    
    def _extraer_compras(self) -> pd.DataFrame:
        """Extrae datos de compras."""
        try:
            # Hacer clic en la pestaña de compras
            self.pagina.click("#tabCompra")
            
            return self._extraer_tabla_actual("compras")
            
        except Exception as e:
            logger.error(f"Error extrayendo compras: {e}")
            return pd.DataFrame()
    
    def _extraer_ventas(self) -> pd.DataFrame:
        """Extrae datos de ventas."""
        try:
            # Hacer clic en la pestaña de ventas
            self.pagina.click('text="VENTA"')
            
            return self._extraer_tabla_actual("ventas")
            
        except Exception as e:
            logger.error(f"Error extrayendo ventas: {e}")
            return pd.DataFrame()
    
    def _extraer_pendientes(self) -> pd.DataFrame:
        """Extrae datos de pendientes."""
        try:
            # Primero ir a compras
            self.pagina.click("#tabCompra")
            
            # Luego a pendientes
            self.pagina.click('text="Pendientes"')
            
            return self._extraer_tabla_actual("pendientes")
            
        except Exception as e:
            logger.error(f"Error extrayendo pendientes: {e}")
            return pd.DataFrame()
    
    def _extraer_tabla_actual(self, tipo: str) -> pd.DataFrame:
        """Extrae la tabla actualmente visible."""
        try:
            # Verificar si hay registros
            if self._verificar_sin_registros():
                logger.info(f"No hay registros de {tipo}")
                return pd.DataFrame()
            
            # Esperar a que cargue la tabla
            self.pagina.wait_for_selector("table", timeout=5000)
            
            # Obtener HTML de la tabla
            tabla_html = self.pagina.locator("table").first.inner_html()
            
            # Convertir a DataFrame usando pandas
            df_list = pd.read_html(f"<table>{tabla_html}</table>")
            
            if df_list:
                df = df_list[0]
                logger.info(f"Extraídos {len(df)} registros de {tipo}")
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error extrayendo tabla de {tipo}: {e}")
            return pd.DataFrame()
    
    def _verificar_sin_registros(self) -> bool:
        """Verifica si hay mensaje de sin registros."""
        try:
            self.pagina.wait_for_timeout(1000)  # Esperar un poco
            return self.pagina.locator(".alert-danger").count() > 0
        except:
            return False
    
    def _capturar_error(self, nombre: str):
        """Captura pantalla de error."""
        self.sesion._capturar_pantalla_error(nombre)


class ExtractorF29:
    """Extractor de datos del Formulario 29."""
    
    def __init__(self, sesion: SesionSIIPlaywright):
        self.sesion = sesion
        self.pagina = sesion.pagina
    
    def extraer_f29_periodo(self, mes: str, año: int) -> Dict[str, any]:
        """
        Extrae información del F29 para un período específico.
        
        Args:
            mes: Nombre del mes (ej: "Enero", "Febrero", etc.)
            año: Año
            
        Returns:
            Diccionario con información del F29
        """
        logger.info(f"Extrayendo F29 para {mes} {año}")
        
        # Navegar a F29
        self.sesion.navegar_a_seccion("f29")
        
        # Extraer tabla de períodos
        estado_periodo = self._obtener_estado_periodo(mes)
        
        resultado = {
            "mes": mes,
            "año": año,
            "estado": estado_periodo,
            "captura_realizada": False
        }
        
        # Si está sin observaciones, capturar formulario
        if estado_periodo == "Declaración sin observaciones.":
            resultado["captura_realizada"] = self._capturar_formulario(mes)
        
        return resultado
    
    def _obtener_estado_periodo(self, mes: str) -> str:
        """Obtiene el estado del período específico."""
        try:
            # Esperar a que cargue la tabla
            self.pagina.wait_for_selector(".gw-tabla-integral_boostrap")
            
            # Obtener tabla HTML
            tabla_html = self.pagina.locator(".gw-tabla-integral_boostrap table").inner_html()
            
            # Convertir a DataFrame
            df_list = pd.read_html(f"<table>{tabla_html}</table>")
            
            if df_list:
                df = df_list[0]
                df = df.dropna(subset=[0])  # Eliminar filas vacías
                
                # Buscar el mes específico
                for idx, row in df.iterrows():
                    if mes.lower() in str(row[0]).lower():
                        return str(row[1]) if len(row) > 1 else "Estado no disponible"
                
                return "Mes no encontrado"
            
            return "No se pudo obtener la tabla"
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del período: {e}")
            return f"Error: {e}"
    
    def _capturar_formulario(self, mes: str) -> bool:
        """Captura el formulario F29 compacto."""
        try:
            # Hacer clic en el mes específico
            mes_locator = self.pagina.locator(f'text="{mes}"').first
            if mes_locator.count() > 0:
                mes_locator.click()
            else:
                logger.warning(f"No se encontró el mes {mes}")
                return False
            
            # Esperar y hacer clic en "Formulario Compacto"
            self.pagina.wait_for_selector('button:has-text("Formulario Compacto")')
            self.pagina.click('button:has-text("Formulario Compacto")')
            
            # Esperar a que se abra la nueva ventana
            with self.pagina.context.expect_page() as nueva_pagina_info:
                pass
            
            nueva_pagina = nueva_pagina_info.value
            nueva_pagina.wait_for_load_state()
            
            # Capturar pantalla
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_captura = self.sesion.config.directorio_capturas / f"F29_{mes}_{timestamp}.png"
            nueva_pagina.screenshot(path=str(archivo_captura))
            
            # Cerrar la nueva ventana
            nueva_pagina.close()
            
            # Volver en la página principal
            self.pagina.click('button:has-text("Volver")')
            
            logger.info(f"Formulario F29 capturado: {archivo_captura}")
            return True
            
        except Exception as e:
            logger.error(f"Error capturando formulario: {e}")
            return False


# Función de conveniencia para uso simple
def extraer_rcv_sii(
    credenciales: CredencialesSII,
    mes: int,
    año: int,
    config: Optional[ConfiguracionSII] = None
) -> Dict[str, pd.DataFrame]:
    """
    Función de conveniencia para extraer RCV del SII.
    
    Args:
        credenciales: Credenciales del SII
        mes: Mes (1-12)
        año: Año
        config: Configuración opcional
        
    Returns:
        Diccionario con DataFrames de compras, ventas y pendientes
    """
    with SesionSIIPlaywright(config) as sesion:
        sesion.iniciar_sesion(credenciales)
        extractor = ExtractorRCV(sesion)
        return extractor.extraer_registro_periodo(mes, año)


# Ejemplo de uso
if __name__ == "__main__":
    # Configuración
    config = ConfiguracionSII(headless=False)
    
    try:
        # Cargar credenciales desde variables de entorno
        credenciales = CredencialesSII.desde_variables_entorno()
    except ValueError:
        # O definir credenciales manualmente (no recomendado para producción)
        credenciales = CredencialesSII(rut="12345678-9", clave="mi_clave")
    
    # Usar context manager para manejo automático de recursos
    with SesionSIIPlaywright(config) as sesion:
        # Iniciar sesión
        sesion.iniciar_sesion(credenciales)
        
        # Extraer RCV
        extractor_rcv = ExtractorRCV(sesion)
        datos_rcv = extractor_rcv.extraer_registro_periodo(mes=1, año=2024)
        
        # Mostrar resultados
        for tipo, df in datos_rcv.items():
            print(f"\n{tipo.upper()}:")
            print(f"Registros: {len(df)}")
            if not df.empty:
                print(df.head())
        
        # Extraer F29
        extractor_f29 = ExtractorF29(sesion)
        datos_f29 = extractor_f29.extraer_f29_periodo("Enero", 2024)
        print(f"\nF29: {datos_f29}")
