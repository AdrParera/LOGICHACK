#!/usr/bin/env python3
"""
Script instalador automático para el Sistema de Gestión de Inventarios
Ejecuta este script una sola vez para configurar todo
"""

import subprocess
import sys
import os
from pathlib import Path

def instalar_dependencias():
    """Instala todas las dependencias necesarias"""
    print("\n" + "="*60)
    print("🚀 Iniciando instalación de dependencias...")
    print("="*60 + "\n")
    
    try:
        # Actualizar pip
        print("📦 Actualizando pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Instalar desde requirements.txt
        print("\n📥 Instalando paquetes necesarios...")
        with open('requirements.txt', 'r') as f:
            paquetes = f.read().strip().split('\n')
        
        for paquete in paquetes:
            if paquete.strip():
                print(f"  ✓ Instalando {paquete}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])
        
        print("\n✅ ¡Dependencias instaladas correctamente!\n")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error durante la instalación: {e}\n")
        return False

def generar_datos_ejemplo():
    """Genera datos de ejemplo"""
    print("="*60)
    print("📊 Generando datos de ejemplo...")
    print("="*60 + "\n")
    
    try:
        exec(open('ejemplo_datos.py').read())
        print("\n✅ Datos de ejemplo generados correctamente!\n")
        return True
    except Exception as e:
        print(f"\n⚠️  No se pudieron generar datos de ejemplo: {e}\n")
        return False

def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "INSTALADOR - Sistema de Gestión de Inventarios" + " "*2 + "║")
    print("╚" + "="*58 + "╝")
    
    # Verificar que estamos en la carpeta correcta
    if not os.path.exists('requirements.txt'):
        print("\n❌ Error: requirements.txt no encontrado.")
        print("   Asegúrate de ejecutar este script en la carpeta del proyecto.")
        sys.exit(1)
    
    # Instalar dependencias
    if not instalar_dependencias():
        sys.exit(1)
    
    # Generar datos de ejemplo
    generar_datos_ejemplo()
    
    print("="*60)
    print("✅ ¡Instalación completada!")
    print("="*60)
    print("\n🚀 Para iniciar el programa, ejecuta:\n")
    
    if sys.platform == "win32":
        print("   run.bat\n")
    else:
        print("   bash run.sh\n")
    
    print("📖 Para más información, lee README.md\n")

if __name__ == "__main__":
    main()
