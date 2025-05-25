# Mi_Libreria

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.40.0+-green.svg)](https://playwright.dev/)

Una librería Python completa para cruces de datos, procesamiento avanzado y automatización del Servicio de Impuestos Internos (SII) de Chile.

## ✨ Lo Nuevo: SII con Playwright

🎉 **Nueva implementación moderna** del módulo SII usando **Playwright** en lugar de Selenium:
- ⚡ **3x más rápido** que Selenium
- 🛡️ **Más estable** y confiable
- 📸 **Capturas automáticas** en errores
- 🔒 **Manejo seguro** de credenciales
- 🌐 **Multi-navegador** (Chromium, Firefox, WebKit)

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)
```bash
python instalar_playwright.py
```

### Opción 2: Manual
```bash
pip install -e .[sii-playwright]
playwright install
```

## 📖 Documentación Completa

📁 **Documentación detallada en [`docs/`](docs/)**:
- [📋 Guía Completa](docs/README.md)
- [🎭 SII con Playwright](docs/SII_PLAYWRIGHT.md)
- [📘 Guía de Uso](docs/USAGE.md)
- [🤝 Contribuir](docs/CONTRIBUTING.md)

## 🎯 Ejemplo Rápido

```python
from Mi_Libreria.SII import CredencialesSII, extraer_rcv_sii

# Configurar credenciales desde variables de entorno
credenciales = CredencialesSII.desde_variables_entorno()

# Extraer RCV con una sola línea
datos = extraer_rcv_sii(credenciales, mes=1, año=2024)

# ¡Listo! Tienes tus datos en DataFrames
print(f"Compras: {len(datos['compras'])} registros")
print(f"Ventas: {len(datos['ventas'])} registros")
```

## 🛠️ Dependencias Principales

- **playwright>=1.40.0** - Automatización web moderna
- **pandas** - Análisis de datos
- **python-dotenv** - Variables de entorno seguras
- **selenium>=4.0.0** - Automatización web clásica (opcional)

## 📦 Módulos Incluidos

| Módulo | Descripción |
|--------|-------------|
| 🔄 **Cruze** | Herramientas para cruces de datos |
| 🗄️ **DB** | Manejo de bases de datos |
| ⚙️ **Funcionalidad** | Utilidades generales |
| 🎯 **Principal** | Funciones principales |
| 🏛️ **SII** | Automatización SII (Selenium + Playwright) |

## 📞 Soporte

¿Necesitas ayuda? Revisa la [documentación completa](docs/) o los [ejemplos](ejemplos_sii_playwright.py).

---
*Construido con ❤️ para automatizar el SII de Chile*
