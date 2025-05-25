"""
Ejemplos de uso del módulo SII con Playwright.

Este archivo muestra diferentes formas de usar el nuevo módulo SII_Playwright
para automatizar tareas del Servicio de Impuestos Internos de Chile.
"""

import os
import asyncio
from pathlib import Path
import pandas as pd
from Mi_Libreria.SII import (
    SesionSIIPlaywright,
    ExtractorRCV,
    ExtractorF29,
    ConfiguracionSII,
    CredencialesSII,
    extraer_rcv_sii
)


def ejemplo_basico_rcv():
    """Ejemplo básico para extraer RCV usando la función de conveniencia."""
    print("🚀 Ejemplo básico - Extracción RCV")
    
    # Configurar credenciales desde variables de entorno
    try:
        credenciales = CredencialesSII.desde_variables_entorno()
    except ValueError:
        print("❌ Variables de entorno SII_RUT y SII_CLAVE no encontradas")
        print("💡 Define las variables o usa credenciales manuales")
        return
    
    # Extraer datos del RCV para enero 2024
    try:
        datos = extraer_rcv_sii(credenciales, mes=1, año=2024)
        
        # Mostrar resultados
        for tipo, df in datos.items():
            print(f"\n📊 {tipo.upper()}: {len(df)} registros")
            if not df.empty:
                print(df.head(3))
                
                # Guardar en Excel
                archivo = Path(f"rcv_{tipo}_enero_2024.xlsx")
                df.to_excel(archivo, index=False)
                print(f"💾 Guardado en: {archivo}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_configuracion_personalizada():
    """Ejemplo con configuración personalizada."""
    print("\n🛠️  Ejemplo con configuración personalizada")
    
    # Configuración personalizada
    config = ConfiguracionSII(
        headless=True,  # Ejecutar sin ventana del navegador
        navegador="firefox",  # Usar Firefox en lugar de Chrome
        timeout_elemento=15000,  # Timeout más largo
        directorio_descargas=Path("./descargas_sii"),
        directorio_capturas=Path("./capturas_sii")
    )
    
    try:
        credenciales = CredencialesSII.desde_variables_entorno()
        
        with SesionSIIPlaywright(config) as sesion:
            print("🔐 Iniciando sesión...")
            sesion.iniciar_sesion(credenciales)
            
            print("📋 Extrayendo RCV...")
            extractor = ExtractorRCV(sesion)
            datos = extractor.extraer_registro_periodo(mes=2, año=2024)
            
            for tipo, df in datos.items():
                print(f"📊 {tipo}: {len(df)} registros")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_multiple_periodos():
    """Ejemplo para extraer múltiples períodos."""
    print("\n📅 Ejemplo múltiples períodos")
    
    try:
        credenciales = CredencialesSII.desde_variables_entorno()
        config = ConfiguracionSII(headless=True)
        
        # Períodos a extraer
        periodos = [
            (1, 2024),  # Enero 2024
            (2, 2024),  # Febrero 2024
            (3, 2024),  # Marzo 2024
        ]
        
        resultados = {}
        
        with SesionSIIPlaywright(config) as sesion:
            sesion.iniciar_sesion(credenciales)
            extractor = ExtractorRCV(sesion)
            
            for mes, año in periodos:
                print(f"📊 Extrayendo {mes:02d}/{año}...")
                
                try:
                    datos = extractor.extraer_registro_periodo(mes, año)
                    resultados[f"{año}_{mes:02d}"] = datos
                    
                    # Resumen
                    total_compras = len(datos['compras'])
                    total_ventas = len(datos['ventas'])
                    total_pendientes = len(datos['pendientes'])
                    
                    print(f"   ✅ Compras: {total_compras}, Ventas: {total_ventas}, Pendientes: {total_pendientes}")
                    
                except Exception as e:
                    print(f"   ❌ Error en {mes:02d}/{año}: {e}")
        
        # Consolidar resultados
        print("\n📈 Consolidando resultados...")
        
        all_compras = []
        all_ventas = []
        
        for periodo, datos in resultados.items():
            if not datos['compras'].empty:
                datos['compras']['periodo'] = periodo
                all_compras.append(datos['compras'])
            
            if not datos['ventas'].empty:
                datos['ventas']['periodo'] = periodo
                all_ventas.append(datos['ventas'])
        
        if all_compras:
            df_compras_consolidado = pd.concat(all_compras, ignore_index=True)
            df_compras_consolidado.to_excel("compras_consolidado.xlsx", index=False)
            print(f"💾 Compras consolidadas: {len(df_compras_consolidado)} registros")
        
        if all_ventas:
            df_ventas_consolidado = pd.concat(all_ventas, ignore_index=True)
            df_ventas_consolidado.to_excel("ventas_consolidado.xlsx", index=False)
            print(f"💾 Ventas consolidadas: {len(df_ventas_consolidado)} registros")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_f29():
    """Ejemplo para extraer información del F29."""
    print("\n📄 Ejemplo F29")
    
    try:
        credenciales = CredencialesSII.desde_variables_entorno()
        config = ConfiguracionSII(headless=False)  # Mostrar ventana para F29
        
        meses = ["Enero", "Febrero", "Marzo"]
        
        with SesionSIIPlaywright(config) as sesion:
            sesion.iniciar_sesion(credenciales)
            extractor = ExtractorF29(sesion)
            
            for mes in meses:
                print(f"📋 Procesando F29 de {mes}...")
                
                try:
                    resultado = extractor.extraer_f29_periodo(mes, 2024)
                    
                    print(f"   Estado: {resultado['estado']}")
                    if resultado['captura_realizada']:
                        print(f"   ✅ Captura realizada")
                    else:
                        print(f"   ⚠️  Sin captura (estado: {resultado['estado']})")
                
                except Exception as e:
                    print(f"   ❌ Error en {mes}: {e}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_credenciales_manuales():
    """Ejemplo usando credenciales definidas manualmente."""
    print("\n🔑 Ejemplo con credenciales manuales")
    
    # ⚠️ IMPORTANTE: No hardcodear credenciales en código de producción
    # Este es solo un ejemplo para testing
    
    rut = input("Ingresa tu RUT (ej: 12345678-9): ").strip()
    clave = input("Ingresa tu clave: ").strip()
    
    if not rut or not clave:
        print("❌ RUT y clave son requeridos")
        return
    
    credenciales = CredencialesSII(rut=rut, clave=clave)
    
    try:
        # Usar solo para una extracción rápida
        datos = extraer_rcv_sii(credenciales, mes=1, año=2024)
        
        print(f"✅ Datos extraídos exitosamente:")
        for tipo, df in datos.items():
            print(f"   {tipo}: {len(df)} registros")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def configurar_variables_entorno():
    """Guía para configurar variables de entorno."""
    print("\n🔧 Configuración de variables de entorno")
    print("Para usar el módulo SII de forma segura, configura las siguientes variables:")
    print()
    print("Windows (PowerShell):")
    print('$env:SII_RUT = "12345678-9"')
    print('$env:SII_CLAVE = "tu_clave_secreta"')
    print()
    print("Windows (CMD):")
    print('set SII_RUT=12345678-9')
    print('set SII_CLAVE=tu_clave_secreta')
    print()
    print("Linux/Mac:")
    print('export SII_RUT="12345678-9"')
    print('export SII_CLAVE="tu_clave_secreta"')
    print()
    print("💡 También puedes crear un archivo .env en tu proyecto")


if __name__ == "__main__":
    print("🤖 Ejemplos del módulo SII con Playwright")
    print("=" * 50)
    
    # Verificar si las variables de entorno están configuradas
    if not os.getenv('SII_RUT') or not os.getenv('SII_CLAVE'):
        print("⚠️  Variables de entorno SII_RUT y SII_CLAVE no encontradas")
        configurar_variables_entorno()
        print("\nEjecuta uno de los siguientes ejemplos después de configurar:")
        print("1. ejemplo_basico_rcv()")
        print("2. ejemplo_configuracion_personalizada()")
        print("3. ejemplo_multiple_periodos()")
        print("4. ejemplo_f29()")
        print("5. ejemplo_credenciales_manuales()")
    else:
        print("✅ Variables de entorno configuradas")
        
        # Ejecutar ejemplo básico
        ejemplo_basico_rcv()
        
        # Descomenta para ejecutar otros ejemplos:
        # ejemplo_configuracion_personalizada()
        # ejemplo_multiple_periodos()
        # ejemplo_f29()
