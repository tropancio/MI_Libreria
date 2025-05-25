"""
Mi_Libreria - Librería Python para cruces de datos y automatización SII

Esta librería proporciona herramientas para:
- Cruces y análisis de datos
- Automatización del SII con Selenium y Playwright
- Procesamiento de bases de datos
- Funcionalidades avanzadas de procesamiento

Dependencias principales:
- playwright>=1.40.0 (para módulo SII moderno)
- pandas, numpy (análisis de datos)
- selenium>=4.0.0 (para módulo SII clásico)
- python-dotenv (manejo seguro de credenciales)
"""

__version__ = "0.1.0"
__author__ = "Tu Nombre"
__description__ = "Librería para cruces de datos, procesamiento avanzado y automatización SII con Playwright"

# Importaciones principales
from .Cruze.Cruze import *
from .DB.DB import *
from .Funcionalidad.Funcionalidad import *
from .Principal.Principal import *
from .SII.SII import *

# Importaciones opcionales de Playwright (si está disponible)
try:
    from .SII.SII_Playwright import (
        SesionSIIPlaywright,
        ExtractorRCV,
        ExtractorF29,
        ConfiguracionSII,
        CredencialesSII,
        extraer_rcv_sii
    )
    __playwright_available__ = True
except ImportError:
    __playwright_available__ = False
    import warnings
    warnings.warn(
        "Playwright no está disponible. Para usar el módulo SII moderno, "
        "instala las dependencias con: pip install playwright>=1.40.0 && playwright install",
        ImportWarning
    )

__all__ = [
    "__version__",
    "__author__", 
    "__description__",
    "__playwright_available__"
]