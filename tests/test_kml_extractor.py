#!/usr/bin/env python3
"""
Script de prueba para el extractor KML

Este script demuestra cómo usar el KMLExtractor programáticamente.
"""

from kml_extractor import KMLExtractor
import sys


def test_kml_extraction():
    """Función de prueba del extractor KML."""
    
    # Ruta al archivo KML de prueba
    # Cambiar esta ruta al archivo KML que se desea probar
    kml_file = "/BMW.kml"
    # Estandarizamos el nombre del archivo de salida basandonos en el nombre del archivo kml
    output_base = kml_file.split(".")[0]
    output_csv = f"{output_base}_extracted.csv"
    output_json = f"{output_base}_extracted.json"
    try:
        print("=== PRUEBA DEL EXTRACTOR KML ===")
        print(f"Procesando archivo: {kml_file}")
        
        # Crear instancia del extractor
        extractor = KMLExtractor(kml_file)
        
        # Extraer datos
        data = extractor.extract_data()
        
        # Mostrar resumen
        extractor.print_summary()
        
        # Guardar en diferentes formatos
        extractor.save_to_csv(f"{output_base}_extracted.csv")
        extractor.save_to_json(f"{output_base}_extracted.json")

        print("\n=== EJEMPLOS DE DATOS EXTRAÍDOS ===")
        for i, item in enumerate(data[:3]):  # Mostrar solo los primeros 3
            print(f"\nRegistro {i+1}:")
            print(f"  Índice: {item['placemark_index']}")
            print(f"  ID: {item['id']}")
            print(f"  Dirección: {item['address']}")
            print(f"  Longitud: {item['longitude']}")
            print(f"  Latitud: {item['latitude']}")
            print(f"  Altitud: {item['altitude']}")
            print(f"  Coordenadas raw: {item['coordinates_raw']}")
        
        print(f"\n✅ Prueba completada exitosamente!")
        print(f"Total de elementos procesados: {len(data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False


if __name__ == "__main__":
    success = test_kml_extraction()
    sys.exit(0 if success else 1)
