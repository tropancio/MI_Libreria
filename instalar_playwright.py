"""
Script de instalación y configuración para el módulo SII con Playwright.

Este script instala las dependencias necesarias y configura Playwright
para uso con el módulo SII.
"""

import subprocess
import sys
import os
from pathlib import Path

def ejecutar_comando(comando, descripcion):
    """Ejecuta un comando y maneja errores."""
    print(f"🔄 {descripcion}...")
    try:
        resultado = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {descripcion} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {descripcion}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def instalar_dependencias():
    """Instala las dependencias de Python."""
    print("📦 Instalando dependencias de Python...")
    
    # Instalar desde requirements
    if not ejecutar_comando(
        "pip install -r requirements_playwright.txt",
        "Instalación de dependencias"
    ):
        # Instalación manual si falla el requirements
        dependencias = [
            "playwright>=1.40.0",
            "pandas>=1.5.0", 
            "python-dotenv>=1.0.0"
        ]
        
        for dep in dependencias:
            ejecutar_comando(f"pip install {dep}", f"Instalando {dep}")

def instalar_navegadores_playwright():
    """Instala los navegadores de Playwright."""
    print("🌐 Instalando navegadores de Playwright...")
    
    # Instalar todos los navegadores
    if not ejecutar_comando(
        "playwright install",
        "Instalación de navegadores"
    ):
        print("⚠️ Error instalando navegadores. Intentando instalar solo Chromium...")
        ejecutar_comando(
            "playwright install chromium",
            "Instalación de Chromium"
        )

def verificar_instalacion():
    """Verifica que la instalación sea correcta."""
    print("🔍 Verificando instalación...")
    
    try:
        import playwright
        print(f"✅ Playwright instalado: versión {playwright.__version__}")
    except ImportError:
        print("❌ Playwright no se pudo importar")
        return False
    
    try:
        import pandas as pd
        print(f"✅ Pandas instalado: versión {pd.__version__}")
    except ImportError:
        print("❌ Pandas no se pudo importar")
        return False
    
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Probar que el navegador esté disponible
            navegador = p.chromium.launch(headless=True)
            navegador.close()
        print("✅ Playwright y navegadores funcionando correctamente")
        return True
    except Exception as e:
        print(f"❌ Error probando Playwright: {e}")
        return False

def crear_archivo_env_ejemplo():
    """Crea un archivo .env de ejemplo."""
    print("📝 Creando archivo .env de ejemplo...")
    
    contenido_env = """# Configuración del SII
# Reemplaza con tus credenciales reales
SII_RUT=12345678-9
SII_CLAVE=tu_clave_secreta

# Configuración opcional
SII_TIMEOUT=10
SII_HEADLESS=false
"""
    
    archivo_env = Path(".env.ejemplo")
    with open(archivo_env, "w", encoding="utf-8") as f:
        f.write(contenido_env)
    
    print(f"✅ Archivo creado: {archivo_env}")
    print("💡 Copia .env.ejemplo a .env y configura tus credenciales")

def mostrar_instrucciones_uso():
    """Muestra instrucciones de uso."""
    print("\n🚀 ¡Instalación completada!")
    print("=" * 50)
    print("📋 Próximos pasos:")
    print()
    print("1. Configura tus credenciales del SII:")
    print("   - Copia .env.ejemplo a .env")
    print("   - Edita .env con tus credenciales reales")
    print()
    print("2. O configura variables de entorno:")
    print("   PowerShell:")
    print('   $env:SII_RUT = "12345678-9"')
    print('   $env:SII_CLAVE = "tu_clave"')
    print()
    print("3. Ejecuta el ejemplo:")
    print("   python ejemplos_sii_playwright.py")
    print()
    print("4. O usa en tu código:")
    print("   from Mi_Libreria.SII import extraer_rcv_sii")
    print()
    print("📚 Documentación adicional en docs/")

def main():
    """Función principal."""
    print("🤖 Instalador del módulo SII con Playwright")
    print("=" * 50)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        return
    
    print(f"✅ Python {sys.version}")
    
    # Paso 1: Instalar dependencias
    instalar_dependencias()
    
    # Paso 2: Instalar navegadores
    instalar_navegadores_playwright()
    
    # Paso 3: Verificar instalación
    if verificar_instalacion():
        print("✅ Verificación exitosa")
    else:
        print("❌ Verificación falló")
        return
    
    # Paso 4: Crear archivo de ejemplo
    crear_archivo_env_ejemplo()
    
    # Paso 5: Mostrar instrucciones
    mostrar_instrucciones_uso()

if __name__ == "__main__":
    main()
