#!/usr/bin/env python3
"""
Instalador de dependencias para Reverse Geocoding Batch Processor
"""

import subprocess
import sys

def install_package(package):
    """Instala un paquete usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} instalado exitosamente")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Error instalando {package}")
        return False

def main():
    print("Instalando dependencias para Reverse Geocoding Batch Processor...")
    print()
    
    packages = [
        "python-dotenv",
        "opencage", 
        "pandas"
    ]
    
    all_success = True
    for package in packages:
        if not install_package(package):
            all_success = False
    
    print()
    if all_success:
        print("✓ Todas las dependencias instaladas exitosamente!")
        print("Ahora puedes usar los scripts de reverse geocoding.")
    else:
        print("✗ Algunas dependencias no se pudieron instalar.")
        print("Por favor, instala manualmente los paquetes faltantes.")

if __name__ == "__main__":
    main()
