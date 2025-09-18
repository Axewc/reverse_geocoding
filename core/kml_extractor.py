#!/usr/bin/env python3
"""
KML Data Extractor

Este módulo proporciona funcionalidades para extraer coordenadas e IDs
de archivos KML generados por BatchGeo o similares.

Autor: Sistema de Reverse Geocoding
Fecha: 2025
"""

import xml.etree.ElementTree as ET
import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KMLExtractor:
    """Extractor de datos de archivos KML."""
    
    def __init__(self, kml_file_path: str):
        """
        Inicializar el extractor KML.
        
        Args:
            kml_file_path (str): Ruta al archivo KML
        """
        self.kml_file_path = Path(kml_file_path)
        self.namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
        self.data = []
        
    def _parse_coordinates(self, coord_text: str) -> Optional[Tuple[float, float, float]]:
        """
        Parsear texto de coordenadas KML.
        
        Args:
            coord_text (str): Texto de coordenadas en formato "lon,lat,alt"
            
        Returns:
            Tuple[float, float, float]: (longitud, latitud, altitud) o None si hay error
        """
        try:
            coords = coord_text.strip().split(',')
            if len(coords) >= 2:
                longitude = float(coords[0])
                latitude = float(coords[1])
                altitude = float(coords[2]) if len(coords) > 2 else 0.0
                return longitude, latitude, altitude
        except (ValueError, IndexError) as e:
            logger.warning(f"Error parseando coordenadas '{coord_text}': {e}")
        return None
    
    def _extract_id_from_extended_data(self, placemark) -> Optional[str]:
        """
        Extraer ID de ExtendedData en un Placemark.
        
        Args:
            placemark: Elemento XML Placemark
            
        Returns:
            str: ID encontrado o None
        """
        extended_data = placemark.find('.//kml:ExtendedData', self.namespace)
        if extended_data is not None:
            data_elements = extended_data.findall('.//kml:Data[@name="id"]', self.namespace)
            for data_elem in data_elements:
                value_elem = data_elem.find('kml:value', self.namespace)
                if value_elem is not None and value_elem.text:
                    return value_elem.text.strip()
        return None
    
    def extract_data(self) -> List[Dict]:
        """
        Extraer todos los datos del archivo KML.
        
        Returns:
            List[Dict]: Lista de diccionarios con los datos extraídos
        """
        if not self.kml_file_path.exists():
            raise FileNotFoundError(f"Archivo KML no encontrado: {self.kml_file_path}")
        
        try:
            tree = ET.parse(self.kml_file_path)
            root = tree.getroot()
            
            # Encontrar todos los Placemarks
            placemarks = root.findall('.//kml:Placemark', self.namespace)
            logger.info(f"Encontrados {len(placemarks)} placemarks en el archivo KML")
            
            extracted_data = []
            
            for i, placemark in enumerate(placemarks):
                placemark_data = {
                    'placemark_index': i + 1,
                    'id': None,
                    'address': None,
                    'longitude': None,
                    'latitude': None,
                    'altitude': None,
                    'coordinates_raw': None
                }
                
                # Extraer ID
                placemark_data['id'] = self._extract_id_from_extended_data(placemark)
                
                # Extraer dirección
                address_elem = placemark.find('kml:address', self.namespace)
                if address_elem is not None and address_elem.text:
                    placemark_data['address'] = address_elem.text.strip()
                
                # Extraer coordenadas
                coordinates_elem = placemark.find('.//kml:coordinates', self.namespace)
                if coordinates_elem is not None and coordinates_elem.text:
                    coord_text = coordinates_elem.text.strip()
                    placemark_data['coordinates_raw'] = coord_text
                    
                    coords = self._parse_coordinates(coord_text)
                    if coords:
                        placemark_data['longitude'] = coords[0]
                        placemark_data['latitude'] = coords[1]
                        placemark_data['altitude'] = coords[2]
                
                # Solo agregar si tiene coordenadas o ID
                if placemark_data['longitude'] is not None or placemark_data['id'] is not None:
                    extracted_data.append(placemark_data)
                    logger.debug(f"Procesado placemark {i+1}: ID={placemark_data['id']}, "
                               f"Coords=({placemark_data['longitude']}, {placemark_data['latitude']})")
            
            self.data = extracted_data
            logger.info(f"Extracción completada: {len(extracted_data)} elementos válidos")
            return extracted_data
            
        except ET.ParseError as e:
            logger.error(f"Error parseando archivo KML: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            raise
    
    def save_to_csv(self, output_file: str) -> None:
        """
        Guardar datos extraídos en formato CSV.
        
        Args:
            output_file (str): Ruta del archivo CSV de salida
        """
        if not self.data:
            logger.warning("No hay datos para guardar. Ejecute extract_data() primero.")
            return
        
        output_path = Path(output_file)
        
        fieldnames = [
            'placemark_index', 'id', 'address', 
            'longitude', 'latitude', 'altitude', 'coordinates_raw'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.data)
        
        logger.info(f"Datos guardados en CSV: {output_path}")
    
    def save_to_json(self, output_file: str) -> None:
        """
        Guardar datos extraídos en formato JSON.
        
        Args:
            output_file (str): Ruta del archivo JSON de salida
        """
        if not self.data:
            logger.warning("No hay datos para guardar. Ejecute extract_data() primero.")
            return
        
        output_path = Path(output_file)
        
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Datos guardados en JSON: {output_path}")
    
    def print_summary(self) -> None:
        """Imprimir resumen de los datos extraídos."""
        if not self.data:
            print("No hay datos para mostrar.")
            return
        
        print(f"\n=== RESUMEN DE EXTRACCIÓN KML ===")
        print(f"Archivo: {self.kml_file_path.name}")
        print(f"Total de elementos: {len(self.data)}")
        
        with_id = sum(1 for item in self.data if item['id'] is not None)
        with_coords = sum(1 for item in self.data if item['longitude'] is not None)
        with_address = sum(1 for item in self.data if item['address'] is not None)
        
        print(f"Elementos con ID: {with_id}")
        print(f"Elementos con coordenadas: {with_coords}")
        print(f"Elementos con dirección: {with_address}")
        
        print(f"\n=== PRIMEROS 5 ELEMENTOS ===")
        for i, item in enumerate(self.data[:5]):
            print(f"\nElemento {i+1}:")
            print(f"  ID: {item['id']}")
            print(f"  Coordenadas: ({item['longitude']}, {item['latitude']})")
            print(f"  Dirección: {item['address']}")


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description='Extractor de coordenadas e IDs de archivos KML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python kml_extractor.py archivo.kml
  python kml_extractor.py archivo.kml --csv salida.csv
  python kml_extractor.py archivo.kml --json salida.json --csv salida.csv
  python kml_extractor.py archivo.kml --verbose
        """
    )
    
    parser.add_argument(
        'kml_file',
        help='Ruta al archivo KML de entrada'
    )
    
    parser.add_argument(
        '--csv',
        help='Guardar resultados en archivo CSV'
    )
    
    parser.add_argument(
        '--json',
        help='Guardar resultados en archivo JSON'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar información detallada'
    )
    
    args = parser.parse_args()
    
    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Crear extractor y procesar archivo
        extractor = KMLExtractor(args.kml_file)
        data = extractor.extract_data()
        
        if not data:
            print("No se encontraron datos válidos en el archivo KML.")
            return 1
        
        # Mostrar resumen
        extractor.print_summary()
        
        # Guardar en formatos solicitados
        if args.csv:
            extractor.save_to_csv(args.csv)
        
        if args.json:
            extractor.save_to_json(args.json)
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        return 1
    except ET.ParseError as e:
        logger.error(f"Error parseando archivo KML: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
