#!/usr/bin/env python3
"""
Ejemplo de Integración del Sistema de Limpieza y Enriquecimiento de Direcciones

Este script demuestra cómo integrar el nuevo sistema con las herramientas existentes
de geocodificación reversa.
"""

import os
import sys
import pandas as pd
from typing import List, Dict

# Añadir el directorio del batch processor al path
current_dir = os.path.dirname(os.path.abspath(__file__))
batch_processor_path = os.path.join(current_dir, 'reverse_geocoding_batch_processor')
sys.path.append(batch_processor_path)

from address_enhancer import AddressEnhancer

def create_sample_data() -> List[Dict]:
    """
    Crea datos de ejemplo que representan casos reales de uso
    """
    return [
        # Direcciones incompletas
        {'id': 1, 'address': 'Gran Vía 25', 'city': 'Madrid'},
        {'id': 2, 'address': 'c/ mayor 15', 'postal_code': '28013'},
        
        # Direcciones con errores de tipeo
        {'id': 3, 'address': 'callle reforma 123', 'city': 'Mexico DF'},
        {'id': 4, 'address': 'avendia insurgentes 456'},
        
        # Direcciones con coordenadas pero sin formato estándar
        {'id': 5, 'address': 'cerca del centro', 'lat': 41.4036, 'lng': 2.1744},
        
        # Direcciones en diferentes idiomas
        {'id': 6, 'address': '123 main st', 'city': 'New York'},
        {'id': 7, 'address': 'champs elysees', 'city': 'Paris'},
        
        # Direcciones muy incompletas
        {'id': 8, 'address': 'Barcelona'},
        {'id': 9, 'address': 'Madrid centro'},
        
        # 🆕 Direcciones con caracteres especiales
        {'id': 10, 'address': 'Sagrada Família!!! @Barcelona (España)', 'postal_code': '123'},
        {'id': 11, 'address': 'Av. Insurgentes #1234 <Colonia Roma>'},
        {'id': 12, 'address': 'Rúa José García López, 42 ~Coruña~'}
    ]

def demonstrate_individual_features(enhancer: AddressEnhancer):
    """
    Demuestra cada funcionalidad del sistema individualmente
    """
    print("="*60)
    print("DEMOSTRACIÓN DE FUNCIONALIDADES INDIVIDUALES")
    print("="*60)
    
    # 1. Detección de direcciones incompletas
    print("\n1. 🔍 DETECCIÓN DE DIRECCIONES INCOMPLETAS")
    print("-" * 50)
    
    test_addresses = ["Gran Vía 25", "123 Main Street, Madrid, 28013", "Barcelona"]
    for addr in test_addresses:
        analysis = enhancer.detect_incomplete_address(addr)
        print(f"'{addr}'")
        print(f"  Completa: {analysis['is_complete']} (Confianza: {analysis['confidence']:.2f})")
        print(f"  Faltantes: {analysis['missing_components']}")
        print()
    
    # 2. Normalización de direcciones
    print("2. ✨ NORMALIZACIÓN DE DIRECCIONES")
    print("-" * 50)
    
    normalize_examples = [
        "c/ gran via 25",
        "av. insurgentes sur 1234", 
        "123 main st",
        "pl. mayor 15"
    ]
    
    for addr in normalize_examples:
        normalized_es = enhancer.normalize_address_format(addr, 'es')
        normalized_en = enhancer.normalize_address_format(addr, 'en')
        print(f"Original: '{addr}'")
        print(f"  Español: '{normalized_es}'")
        print(f"  English: '{normalized_en}'")
        print()
    
    # 3. Sugerencias de corrección
    print("3. 🔧 SUGERENCIAS DE CORRECCIÓN")
    print("-" * 50)
    
    error_examples = ["callle mayor 25", "avendia reforma", "123 main stret"]
    for addr in error_examples:
        suggestions = enhancer.suggest_address_corrections(addr)
        print(f"'{addr}' → {suggestions}")
    print()
    
    # 4. Validación de códigos postales
    print("4. ✅ VALIDACIÓN DE CÓDIGOS POSTALES")
    print("-" * 50)
    
    postal_examples = [
        ("28013", "ES"), ("12345", "US"), ("K1A 0A9", "CA"), ("123", "ES")
    ]
    
    for postal, country in postal_examples:
        validation = enhancer.validate_postal_code(postal, country)
        print(f"{postal} ({country}): {'✅' if validation['is_valid'] else '❌'}")
    print()
    
    # 5. 🆕 Limpieza de caracteres especiales
    print("5. 🧽 LIMPIEZA DE CARACTERES ESPECIALES")
    print("-" * 50)
    
    from reverse_geocoding_batch_processor.address_enhancer import clean_address_text
    
    special_char_examples = [
        "Calle Mayor!!! @Madrid (España)",
        "Av. Insurgentes #1234 <México>",
        "Rúa José García López, 42 ~Coruña~"
    ]
    
    for addr in special_char_examples:
        clean_conservative = clean_address_text(addr, aggressive=False)
        clean_aggressive = clean_address_text(addr, aggressive=True)
        print(f"Original:      '{addr}'")
        print(f"Conservadora:  '{clean_conservative}'")
        print(f"Agresiva:      '{clean_aggressive}'")
        print()

def demonstrate_batch_processing(enhancer: AddressEnhancer):
    """
    Demuestra el procesamiento en lote completo
    """
    print("="*60)
    print("DEMOSTRACIÓN DE PROCESAMIENTO EN LOTE")
    print("="*60)
    
    # Crear datos de muestra
    sample_data = create_sample_data()
    
    print(f"\n📋 Procesando {len(sample_data)} direcciones de ejemplo...")
    print("\nDatos de entrada:")
    df_input = pd.DataFrame(sample_data)
    print(df_input[['id', 'address']].to_string(index=False))
    
    # Procesar en lote
    print(f"\n⚙️ Iniciando procesamiento...")
    enhanced_addresses = enhancer.process_address_batch(
        sample_data, 
        delay=0.5,  # Delay corto para demo
        language='es',
        clean_special_chars=True,  # 🆕 Activar limpieza de caracteres especiales
        aggressive=False  # 🆕 Usar limpieza conservadora
    )
    
    print(f"\n🧽 Procesamiento incluye limpieza conservadora de caracteres especiales")
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS DEL PROCESAMIENTO:")
    print("-" * 50)
    
    for addr in enhanced_addresses:
        print(f"ID {addr['id']}:")
        print(f"  Original: {addr.get('address', 'N/A')}")
        print(f"  Completada: {addr.get('completed_address', 'N/A')}")
        print(f"  Normalizada: {addr.get('normalized_address', 'N/A')}")
        print(f"  Método: {addr.get('method_used', 'N/A')}")
        
        if 'quality_metrics' in addr:
            metrics = addr['quality_metrics']
            print(f"  Calidad: {metrics['completeness_score']:.2f}")
        
        if 'coordinates' in addr:
            coords = addr['coordinates']
            print(f"  Coordenadas: ({coords['lat']:.4f}, {coords['lng']:.4f})")
        
        if 'administrative_levels' in addr:
            admin = addr['administrative_levels']
            print(f"  Ubicación: {admin.get('city', 'N/A')}, {admin.get('country', 'N/A')}")
        
        print()
    
    return enhanced_addresses

def demonstrate_cleaning_options(enhancer: AddressEnhancer):
    """
    Demuestra específicamente las opciones de limpieza de caracteres especiales
    """
    print("="*60)
    print("DEMOSTRACIÓN DE OPCIONES DE LIMPIEZA")
    print("="*60)
    
    # Datos de prueba con caracteres especiales
    test_data = [
        {'id': 1, 'address': 'Calle Mayor!!! @Madrid (España)'},
        {'id': 2, 'address': 'Av. Insurgentes #1234 <México>'},
        {'id': 3, 'address': 'Rúa José García López, 42 ~Coruña~'}
    ]
    
    print("Datos de prueba:")
    for item in test_data:
        print(f"  {item['id']}. '{item['address']}'")
    
    # Procesamiento SIN limpieza
    print(f"\n🔍 PROCESAMIENTO SIN LIMPIEZA:")
    print("-" * 40)
    no_clean = enhancer.process_address_batch(
        test_data.copy(), delay=0.2, language='es', 
        clean_special_chars=False
    )
    for addr in no_clean:
        print(f"  {addr['id']}. '{addr.get('completed_address', addr.get('address', 'N/A'))}'")
    
    # Procesamiento CON limpieza conservadora
    print(f"\n🧽 PROCESAMIENTO CON LIMPIEZA CONSERVADORA:")
    print("-" * 40)
    conservative_clean = enhancer.process_address_batch(
        test_data.copy(), delay=0.2, language='es', 
        clean_special_chars=True, aggressive=False
    )
    for addr in conservative_clean:
        print(f"  {addr['id']}. '{addr.get('completed_address', addr.get('address', 'N/A'))}'")
    
    # Procesamiento CON limpieza agresiva
    print(f"\n🔥 PROCESAMIENTO CON LIMPIEZA AGRESIVA:")
    print("-" * 40)
    aggressive_clean = enhancer.process_address_batch(
        test_data.copy(), delay=0.2, language='es', 
        clean_special_chars=True, aggressive=True
    )
    for addr in aggressive_clean:
        print(f"  {addr['id']}. '{addr.get('completed_address', addr.get('address', 'N/A'))}'")
    
    print(f"\n📝 OBSERVACIONES:")
    print("  • Sin limpieza: Se preservan todos los caracteres especiales")
    print("  • Conservadora: Se eliminan símbolos (!, @, #, <>, ~) pero se mantienen acentos")
    print("  • Agresiva: Se eliminan símbolos Y acentos para compatibilidad con sistemas legacy")

def demonstrate_integration_with_existing_tools(enhancer: AddressEnhancer):
    """
    Demuestra cómo el nuevo sistema se integra con las herramientas existentes
    """
    print("="*60)
    print("INTEGRACIÓN CON HERRAMIENTAS EXISTENTES")
    print("="*60)
    
    # Simular datos del sistema de geocodificación reversa existente
    existing_reverse_geocoding_results = [
        {
            'latitude': 40.4168,
            'longitude': -3.7038,
            'address': 'Madrid, España',
            'city': 'Madrid',
            'country': 'España'
        },
        {
            'latitude': 41.4036,
            'longitude': 2.1744,
            'address': 'Barcelona, España', 
            'city': 'Barcelona',
            'country': 'España'
        }
    ]
    
    print("\n🔄 Enriqueciendo resultados de geocodificación reversa existente...")
    
    for i, result in enumerate(existing_reverse_geocoding_results, 1):
        print(f"\n--- Resultado {i} ---")
        print(f"Datos originales: {result}")
        
        # Enriquecer usando el nuevo sistema
        coordinates = (result['latitude'], result['longitude'])
        enriched = enhancer.enrich_location_data(result, coordinates)
        
        print(f"\nDatos enriquecidos añadidos:")
        if 'timezone' in enriched:
            print(f"  Zona horaria: {enriched['timezone']['name']}")
        
        if 'geographic_info' in enriched:
            geo = enriched['geographic_info']
            print(f"  Código postal: {geo.get('postcode', 'N/A')}")
            print(f"  Continente: {geo.get('continent', 'N/A')}")
            print(f"  Moneda: {geo.get('currency', {}).get('name', 'N/A')}")
        
        if 'administrative_levels' in enriched:
            admin = enriched['administrative_levels']
            print(f"  Provincia: {admin.get('state', 'N/A')}")
            print(f"  Barrio: {admin.get('neighbourhood', 'N/A')}")

def export_results_demonstration(enhancer: AddressEnhancer, addresses: List[Dict]):
    """
    Demuestra las opciones de exportación
    """
    print("="*60)
    print("DEMOSTRACIÓN DE EXPORTACIÓN")
    print("="*60)
    
    # Exportar a CSV
    csv_file = 'demo_enhanced_addresses.csv'
    enhancer.export_enhanced_addresses(addresses, csv_file, 'csv')
    
    print(f"\n📄 Exportado a CSV: {csv_file}")
    
    # Mostrar estadísticas del archivo CSV
    df = pd.read_csv(csv_file)
    print(f"  Filas: {len(df)}")
    print(f"  Columnas: {len(df.columns)}")
    print(f"  Primeras 5 columnas: {list(df.columns[:5])}")
    
    # Exportar a JSON
    json_file = 'demo_enhanced_addresses.json'
    enhancer.export_enhanced_addresses(addresses, json_file, 'json')
    
    print(f"\n📋 Exportado a JSON: {json_file}")
    
    # Mostrar tamaño de archivos
    csv_size = os.path.getsize(csv_file)
    json_size = os.path.getsize(json_file)
    
    print(f"  Tamaño CSV: {csv_size:,} bytes")
    print(f"  Tamaño JSON: {json_size:,} bytes")

def main():
    """
    Función principal que ejecuta todas las demostraciones
    """
    print("🚀 DEMOSTRACIÓN COMPLETA DEL SISTEMA DE LIMPIEZA Y ENRIQUECIMIENTO")
    print("🔗 Integrado con OpenCage Geocoding API")
    print()
    
    try:
        # Inicializar el enhancer
        print("⚙️ Inicializando AddressEnhancer...")
        enhancer = AddressEnhancer()
        print("✅ Sistema inicializado correctamente")
        
        # Ejecutar demostraciones
        demonstrate_individual_features(enhancer)
        enhanced_addresses = demonstrate_batch_processing(enhancer)
        demonstrate_cleaning_options(enhancer)  # 🆕 Nueva demostración
        demonstrate_integration_with_existing_tools(enhancer)
        export_results_demonstration(enhancer, enhanced_addresses)
        
        print("\n" + "="*60)
        print("🎉 ¡DEMOSTRACIÓN COMPLETADA EXITOSAMENTE!")
        print("="*60)
        print("\n📚 Para más ejemplos interactivos, abre:")
        print("   address_enhancement_demo.ipynb")
        print("\n🔧 Para usar desde línea de comandos:")
        print("   python reverse_geocoding_batch_processor/address_enhancer.py input.csv -o output.csv")
        print("\n💻 Para uso programático, importa:")
        print("   from reverse_geocoding_batch_processor.address_enhancer import AddressEnhancer")
        
    except Exception as e:
        print(f"❌ Error durante la demostración: {e}")
        print("\n🔍 Verifica que:")
        print("   1. El archivo .env existe con tu OPENCAGE_API_KEY")
        print("   2. Las dependencias están instaladas (ejecuta install_dependencies.py)")
        print("   3. Tienes conexión a internet")

if __name__ == "__main__":
    main()
