# Módulo SII con Playwright

## Descripción

El módulo `SII_Playwright` es una implementación moderna para automatización del Servicio de Impuestos Internos de Chile usando **Playwright** en lugar de Selenium. 

## Ventajas de Playwright sobre Selenium

✅ **Más rápido y estable**: Playwright está optimizado para aplicaciones web modernas  
✅ **Mejor manejo de contenido dinámico**: Esperas inteligentes automáticas  
✅ **Capturas automáticas en errores**: Debug más fácil  
✅ **Soporte multi-navegador**: Chromium, Firefox, Safari  
✅ **API más moderna**: Sintaxis más limpia y legible  
✅ **Mejor documentación**: Documentación oficial excelente  

## Instalación

### Opción 1: Script automático
```bash
python instalar_playwright.py
```

### Opción 2: Manual
```bash
# Instalar dependencias
pip install -r requirements_playwright.txt

# Instalar navegadores de Playwright
playwright install
```

## Configuración

### Variables de Entorno (Recomendado)

**PowerShell:**
```powershell
$env:SII_RUT = "12345678-9"
$env:SII_CLAVE = "tu_clave_secreta"
```

**CMD:**
```cmd
set SII_RUT=12345678-9
set SII_CLAVE=tu_clave_secreta
```

**Linux/Mac:**
```bash
export SII_RUT="12345678-9"
export SII_CLAVE="tu_clave_secreta"
```

### Archivo .env
```env
SII_RUT=12345678-9
SII_CLAVE=tu_clave_secreta
SII_TIMEOUT=10
SII_HEADLESS=false
```

## Uso Básico

### Extracción Rápida de RCV
```python
from Mi_Libreria.SII import extraer_rcv_sii, CredencialesSII

# Cargar credenciales desde variables de entorno
credenciales = CredencialesSII.desde_variables_entorno()

# Extraer RCV de enero 2024
datos = extraer_rcv_sii(credenciales, mes=1, año=2024)

# Acceder a los datos
compras_df = datos['compras']
ventas_df = datos['ventas']
pendientes_df = datos['pendientes']

print(f"Compras: {len(compras_df)} registros")
print(f"Ventas: {len(ventas_df)} registros")
```

### Uso Avanzado con Context Manager
```python
from Mi_Libreria.SII import (
    SesionSIIPlaywright, 
    ExtractorRCV, 
    ConfiguracionSII,
    CredencialesSII
)

# Configuración personalizada
config = ConfiguracionSII(
    headless=True,  # Sin ventana del navegador
    navegador="firefox",  # Usar Firefox
    timeout_elemento=15000,  # 15 segundos de timeout
)

credenciales = CredencialesSII.desde_variables_entorno()

# Usar context manager para limpieza automática
with SesionSIIPlaywright(config) as sesion:
    # Iniciar sesión
    sesion.iniciar_sesion(credenciales)
    
    # Crear extractor
    extractor = ExtractorRCV(sesion)
    
    # Extraer múltiples períodos
    periodos = [(1, 2024), (2, 2024), (3, 2024)]
    
    for mes, año in periodos:
        datos = extractor.extraer_registro_periodo(mes, año)
        
        # Guardar en Excel
        if not datos['compras'].empty:
            datos['compras'].to_excel(f"compras_{año}_{mes:02d}.xlsx", index=False)
```

### Extracción de F29
```python
from Mi_Libreria.SII import ExtractorF29

with SesionSIIPlaywright() as sesion:
    sesion.iniciar_sesion(credenciales)
    
    extractor_f29 = ExtractorF29(sesion)
    
    meses = ["Enero", "Febrero", "Marzo"]
    for mes in meses:
        resultado = extractor_f29.extraer_f29_periodo(mes, 2024)
        
        print(f"{mes}: {resultado['estado']}")
        if resultado['captura_realizada']:
            print(f"  ✅ Captura guardada")
```

## Clases Principales

### `ConfiguracionSII`
Configuración para la automatización del SII.

```python
config = ConfiguracionSII(
    timeout_navegacion=30000,  # Timeout para navegación (ms)
    timeout_elemento=10000,    # Timeout para elementos (ms)
    headless=False,           # Mostrar ventana del navegador
    navegador="chromium",     # chromium, firefox, webkit
    directorio_descargas=Path("./descargas"),
    directorio_capturas=Path("./capturas")
)
```

### `CredencialesSII`
Manejo seguro de credenciales.

```python
# Desde variables de entorno (recomendado)
credenciales = CredencialesSII.desde_variables_entorno()

# Manual (solo para testing)
credenciales = CredencialesSII(rut="12345678-9", clave="mi_clave")
```

### `SesionSIIPlaywright`
Maneja la sesión web del SII.

```python
with SesionSIIPlaywright(config) as sesion:
    sesion.iniciar_sesion(credenciales)
    sesion.navegar_a_seccion("rcv")
    sesion.cerrar_sesion()
```

### `ExtractorRCV`
Extrae datos de Registro de Compras y Ventas.

```python
extractor = ExtractorRCV(sesion)
datos = extractor.extraer_registro_periodo(mes=1, año=2024)

# Retorna diccionario con:
# - 'compras': DataFrame con compras
# - 'ventas': DataFrame con ventas  
# - 'pendientes': DataFrame con pendientes
```

### `ExtractorF29`
Extrae información del Formulario 29.

```python
extractor = ExtractorF29(sesion)
resultado = extractor.extraer_f29_periodo("Enero", 2024)

# Retorna diccionario con:
# - 'mes': Mes consultado
# - 'año': Año consultado
# - 'estado': Estado del formulario
# - 'captura_realizada': Si se capturó el formulario
```

## Manejo de Errores

El módulo incluye manejo robusto de errores:

- **Capturas automáticas**: En caso de error se guardan capturas de pantalla
- **Logging detallado**: Información de debug en consola
- **Timeouts configurables**: Evita que el script se cuelgue
- **Context managers**: Limpieza automática de recursos

## Comparación con Módulo Original

| Característica | Selenium (Original) | Playwright (Nuevo) |
|---|---|---|
| Velocidad | ⚡ Medio | ⚡⚡⚡ Rápido |
| Estabilidad | ⚠️ Variable | ✅ Alta |
| Manejo de errores | ❌ Básico | ✅ Avanzado |
| Capturas de debug | ❌ Manual | ✅ Automático |
| Multi-navegador | ⚡ Limitado | ✅ Completo |
| Sintaxis | 📝 Verbosa | 📝 Limpia |
| Mantenimiento | ⚠️ Alto | ✅ Bajo |

## Migración desde Selenium

Si actualmente usas el módulo `SII.py` original, la migración es sencilla:

```python
# Antes (Selenium)
from Mi_Libreria.SII import Pagina, Procesos

pagina = Pagina()
pagina.Login([rut, clave])
procesos = Procesos(pagina)
datos = procesos.Compra_Venta([mes, año])

# Después (Playwright)  
from Mi_Libreria.SII import extraer_rcv_sii, CredencialesSII

credenciales = CredencialesSII(rut, clave)
datos = extraer_rcv_sii(credenciales, mes, año)
```

## Ejemplos Completos

Revisa el archivo `ejemplos_sii_playwright.py` para ver ejemplos completos de:

- ✅ Extracción básica de RCV
- ✅ Configuración personalizada
- ✅ Extracción de múltiples períodos
- ✅ Extracción de F29
- ✅ Manejo de credenciales

## Troubleshooting

### Error: "playwright not found"
```bash
pip install playwright
playwright install
```

### Error: "Credenciales no encontradas"
Asegúrate de configurar las variables de entorno:
```bash
$env:SII_RUT = "tu_rut"
$env:SII_CLAVE = "tu_clave"
```

### Error de timeout
Aumenta los timeouts en la configuración:
```python
config = ConfiguracionSII(
    timeout_navegacion=60000,  # 60 segundos
    timeout_elemento=20000     # 20 segundos
)
```

### Navegador no se cierra
Usa siempre context managers:
```python
with SesionSIIPlaywright() as sesion:
    # tu código aquí
    pass  # El navegador se cierra automáticamente
```

## Soporte

Para problemas o sugerencias:
1. Revisa los logs en consola
2. Verifica las capturas de pantalla en `./capturas/`
3. Consulta la documentación de Playwright: https://playwright.dev/python/
