# Mi_Libreria

Una librería Python completa para cruces de datos, procesamiento avanzado y automatización del Servicio de Impuestos Internos (SII) de Chile.

## 🚀 Características

- **Cruces de Datos**: Herramientas avanzadas para el cruce y análisis de datasets
- **Procesamiento de Bases de Datos**: Módulo para manejo eficiente de bases de datos
- **Funcionalidades Avanzadas**: Utilidades para procesamiento de datos
- **Automatización SII**: Módulos para automatización web del SII con soporte para:
  - **Selenium** (implementación clásica)
  - **Playwright** (implementación moderna) ⭐ **NUEVO**

## 📦 Dependencias Principales

### Core Dependencies
- `pandas` - Manipulación y análisis de datos
- `numpy` - Computación numérica
- `IPython` - Interfaz interactiva mejorada
- `ipywidgets` - Widgets interactivos para Jupyter
- `ipydatagrid` - Grillas de datos avanzadas

### SII Automation Dependencies
- `playwright>=1.40.0` - Automatización web moderna (recomendado)
- `selenium>=4.0.0` - Automatización web clásica
- `python-dotenv>=1.0.0` - Manejo seguro de variables de entorno
- `pyodbc>=4.0.0` - Conectividad con bases de datos

## 🎯 Módulos Incluidos

1. **Cruze** - Herramientas para cruces de datos
2. **DB** - Manejo de bases de datos
3. **Funcionalidad** - Utilidades generales
4. **Principal** - Funciones principales
5. **SII** - Automatización del SII (Selenium + Playwright)

## ⚡ Quick Start

### Instalación Básica
```bash
pip install -e .
```

### Instalación con Playwright (Recomendado para SII)
```bash
pip install -e .[sii-playwright]
playwright install
```

### Instalación Completa con Herramientas de Desarrollo
```bash
pip install -e .[sii-playwright,dev]
```

## 🎪 Ejemplo de Uso - SII con Playwright

```python
from Mi_Libreria.SII import CredencialesSII, extraer_rcv_sii

# Configurar credenciales (usando variables de entorno)
credenciales = CredencialesSII.desde_variables_entorno()

# Extraer RCV de enero 2024
datos = extraer_rcv_sii(credenciales, mes=1, año=2024)

# Procesar resultados
for tipo, df in datos.items():
    print(f"{tipo}: {len(df)} registros")
```

## 📚 Documentación

- [Guía de Uso](USAGE.md)
- [Guía de Contribución](CONTRIBUTING.md)
- [Módulo SII con Playwright](SII_PLAYWRIGHT.md)
- [Mejoras Sugeridas](MEJORAS_SUGERIDAS.md)

## 🔧 Desarrollo

Para configurar el entorno de desarrollo:

```bash
git clone <repository>
cd MI_Libreria
pip install -e .[dev]
pytest tests/
```
