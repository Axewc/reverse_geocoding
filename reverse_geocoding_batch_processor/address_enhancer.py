#!/usr/bin/env python3
"""
Sistema de Limpieza y Enriquecimiento de Datos de Direcciones
Integrado con OpenCage Geocoding API

Este módulo implementa las funcionalidades descritas en rules.md:
1. Sistema de Completado Inteligente de Direcciones
2. Validador y Normalizador de Direcciones
3. Sistema de Enriquecimiento de Datos Geográficos
"""

import csv
import pandas as pd
import os
import re
import time
from typing import List, Dict, Optional, Tuple, Union
from dotenv import load_dotenv
from opencage.geocoder import OpenCageGeocode
import difflib
from datetime import datetime

def clean_address_text(text: str, aggressive: bool = False) -> str:
    """
    Clean special characters from address text while preserving language-specific characters
    
    Args:
        text (str): Text to clean
        aggressive (bool): If True, also removes some accented characters for compatibility
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return text
    
    if aggressive:
        # More aggressive cleaning - removes some accented characters for compatibility
        # This is useful for systems that don't handle Unicode well
        cleaned = re.sub(r'[?¿!¡@#$%^&*()_+=<>{}[\]|\\/:;"\'`~]', '', text)
        # Replace common accented characters with their basic equivalents
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
            'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
            'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
            'ã': 'a', 'ẽ': 'e', 'ĩ': 'i', 'õ': 'o', 'ũ': 'u',
            'ñ': 'n', 'ç': 'c', 'ß': 'ss'
        }
        for accented, basic in replacements.items():
            cleaned = cleaned.replace(accented, basic)
    else:
        # Conservative cleaning - preserves all accented characters
        # Only removes problematic symbols that can cause issues in data processing
        cleaned = re.sub(r'[?¿!¡@#$%^&*()_+=<>{}[\]|\\/:;"\'`~]', '', text)
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned

class AddressEnhancer:
    """
    Clase principal para limpiar, validar y enriquecer datos de direcciones
    """
    
    def __init__(self, api_key: str = None):
        """
        Inicializa el enhancer con la API key de OpenCage
        """
        if not api_key:
            load_dotenv()
            api_key = os.getenv('OPENCAGE_API_KEY')
            if not api_key:
                raise ValueError("OPENCAGE_API_KEY not found in environment variables or .env file")
        
        self.geocoder = OpenCageGeocode(api_key)
        self.common_abbreviations = {
            # Español
            'calle': ['c/', 'c\\', 'cl', 'cl.', 'call'],
            'avenida': ['av', 'av.', 'avda', 'avda.', 'aven'],
            'plaza': ['pl', 'pl.', 'plz'],
            'paseo': ['ps', 'ps.', 'pso'],
            'carrera': ['cr', 'cr.', 'cra', 'cra.'],
            'diagonal': ['dg', 'dg.', 'diag'],
            'transversal': ['tv', 'tv.', 'trans'],
            # English
            'street': ['st', 'st.', 'str', 'str.'],
            'avenue': ['ave', 'ave.', 'av'],
            'boulevard': ['blvd', 'blvd.', 'boul'],
            'road': ['rd', 'rd.'],
            'drive': ['dr', 'dr.'],
            'lane': ['ln', 'ln.'],
            'court': ['ct', 'ct.'],
            'place': ['pl', 'pl.']
        }
    
    def normalize_address_format(self, address: str, target_language: str = 'es') -> str:
        """
        Normaliza el formato de direcciones estandarizando abreviaciones
        
        Args:
            address (str): Dirección a normalizar
            target_language (str): Idioma objetivo ('es' o 'en')
        
        Returns:
            str: Dirección normalizada
        """
        if not address:
            return address
            
        normalized = address.lower().strip()
        
        # Normalizar abreviaciones según el idioma objetivo
        for full_word, abbreviations in self.common_abbreviations.items():
            # Si el idioma objetivo es español, usamos palabras completas en español
            if target_language == 'es' and full_word in ['calle', 'avenida', 'plaza', 'paseo', 'carrera', 'diagonal', 'transversal']:
                for abbrev in abbreviations:
                    # Reemplazar abreviaciones con palabra completa
                    pattern = r'\b' + re.escape(abbrev) + r'\b'
                    normalized = re.sub(pattern, full_word, normalized, flags=re.IGNORECASE)
            
            # Si el idioma objetivo es inglés, usamos palabras completas en inglés
            elif target_language == 'en' and full_word in ['street', 'avenue', 'boulevard', 'road', 'drive', 'lane', 'court', 'place']:
                for abbrev in abbreviations:
                    pattern = r'\b' + re.escape(abbrev) + r'\b'
                    normalized = re.sub(pattern, full_word, normalized, flags=re.IGNORECASE)
        
        # Capitalizar primera letra de cada palabra
        normalized = ' '.join(word.capitalize() for word in normalized.split())
        
        # Limpiar espacios múltiples
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def detect_incomplete_address(self, address: str) -> Dict[str, Union[bool, List[str]]]:
        """
        Detecta si una dirección está incompleta y qué componentes faltan
        
        Args:
            address (str): Dirección a analizar
        
        Returns:
            Dict: Información sobre completitud de la dirección
        """
        if not address:
            return {
                'is_complete': False,
                'missing_components': ['address'],
                'confidence': 0.0
            }
        
        address_lower = address.lower()
        missing_components = []
        
        # Componentes esperados en una dirección completa
        has_street_number = bool(re.search(r'\d+', address))
        has_street_name = bool(re.search(r'(calle|avenida|street|avenue|road|drive|c/|av|st|rd)', address_lower))
        has_city = len(address.split(',')) > 1  # Aproximación simple
        has_postal_code = bool(re.search(r'\b\d{5}(-\d{4})?\b|\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b', address))
        
        if not has_street_number:
            missing_components.append('street_number')
        if not has_street_name:
            missing_components.append('street_name')
        if not has_city:
            missing_components.append('city')
        if not has_postal_code:
            missing_components.append('postal_code')
        
        # Calcular confianza basada en componentes presentes
        total_components = 4
        present_components = total_components - len(missing_components)
        confidence = present_components / total_components
        
        return {
            'is_complete': len(missing_components) == 0,
            'missing_components': missing_components,
            'confidence': confidence,
            'components_found': {
                'street_number': has_street_number,
                'street_name': has_street_name,
                'city': has_city,
                'postal_code': has_postal_code
            }
        }
    
    def suggest_address_corrections(self, address: str, max_suggestions: int = 3) -> List[str]:
        """
        Sugiere correcciones para errores comunes en direcciones
        
        Args:
            address (str): Dirección original
            max_suggestions (int): Número máximo de sugerencias
        
        Returns:
            List[str]: Lista de direcciones corregidas sugeridas
        """
        if not address:
            return []
        
        suggestions = []
        
        # Correcciones comunes
        common_corrections = {
            # Errores de tipeo comunes en español
            'callle': 'calle',
            'avenída': 'avenida',
            'avendia': 'avenida',
            'plasa': 'plaza',
            'carrrera': 'carrera',
            # Errores en inglés
            'stret': 'street',
            'streat': 'street',
            'avenu': 'avenue',
            'boulvard': 'boulevard'
        }
        
        corrected = address.lower()
        for error, correction in common_corrections.items():
            if error in corrected:
                corrected = corrected.replace(error, correction)
                suggestions.append(corrected.title())
        
        # Normalizar formato
        normalized = self.normalize_address_format(address)
        if normalized != address and normalized not in suggestions:
            suggestions.append(normalized)
        
        return suggestions[:max_suggestions]
    
    def complete_address(self, partial_address: str, coordinates: Tuple[float, float] = None, 
                        language: str = 'es', clean_special_chars: bool = False, 
                        aggressive: bool = False) -> Dict[str, Union[str, Dict]]:
        """
        Completa direcciones parciales usando diferentes estrategias
        
        Args:
            partial_address (str): Dirección parcial
            coordinates (Tuple[float, float]): Coordenadas opcionales (lat, lng)
            language (str): Idioma para los resultados
            clean_special_chars (bool): Si True, limpia caracteres especiales de las direcciones
            aggressive (bool): Si True, usa limpieza agresiva (también elimina caracteres acentuados)
        
        Returns:
            Dict: Dirección completada con metadatos
        """
        result = {
            'original_address': partial_address,
            'completed_address': partial_address,
            'method_used': 'none',
            'confidence': 0.0,
            'components': {},
            'suggestions': []
        }
        
        try:
            # Estrategia 1: Si tienes coordenadas, usa geocodificación inversa
            if coordinates:
                lat, lng = coordinates
                
                # Añadir parámetros para controlar formato de respuesta
                params = {}
                if clean_special_chars:
                    params['no_annotations'] = 1
                
                reverse_result = self.geocoder.reverse_geocode(lat, lng, language=language, **params)
                
                if reverse_result:
                    full_address = reverse_result[0]['formatted']
                    components = reverse_result[0].get('components', {})
                    
                    # Limpiar caracteres especiales si se solicita
                    if clean_special_chars:
                        full_address = clean_address_text(full_address, aggressive)
                        # Limpiar también los componentes
                        for key, value in components.items():
                            if isinstance(value, str):
                                components[key] = clean_address_text(value, aggressive)
                    
                    # Mezclar datos de dirección parcial con dirección completa
                    merged_address = self._merge_address_data(partial_address, full_address, components)
                    
                    result.update({
                        'completed_address': merged_address,
                        'method_used': 'reverse_geocoding',
                        'confidence': 0.9,
                        'components': components
                    })
                    
                    return result
            
            # Estrategia 2: Usar geocodificación directa para completar
            if partial_address.strip():
                geocode_result = self.geocoder.geocode(partial_address, language=language)
                
                if geocode_result:
                    full_address = geocode_result[0]['formatted']
                    components = geocode_result[0].get('components', {})
                    confidence = geocode_result[0].get('confidence', 5) / 10.0  # Normalizar a 0-1
                    
                    # Limpiar caracteres especiales si se solicita
                    if clean_special_chars:
                        full_address = clean_address_text(full_address, aggressive)
                        # Limpiar también los componentes
                        for key, value in components.items():
                            if isinstance(value, str):
                                components[key] = clean_address_text(value, aggressive)
                    
                    result.update({
                        'completed_address': full_address,
                        'method_used': 'forward_geocoding',
                        'confidence': min(confidence, 0.8),  # Máximo 0.8 para geocodificación directa
                        'components': components,
                        'coordinates': {
                            'lat': geocode_result[0]['geometry']['lat'],
                            'lng': geocode_result[0]['geometry']['lng']
                        }
                    })
            
            # Añadir sugerencias de corrección
            result['suggestions'] = self.suggest_address_corrections(partial_address)
            
        except Exception as e:
            result['error'] = str(e)
            result['method_used'] = 'error'
        
        return result
    
    def _merge_address_data(self, partial_address: str, full_address: str, components: Dict) -> str:
        """
        Mezcla datos de dirección parcial con dirección completa obtenida por geocodificación
        """
        if not partial_address.strip():
            return full_address
        
        # Si la dirección parcial contiene información específica (como número de casa)
        # que no está en la dirección completa, intentamos combinarlas
        partial_words = set(partial_address.lower().split())
        full_words = set(full_address.lower().split())
        
        # Si la dirección parcial tiene palabras que no están en la completa
        unique_partial_words = partial_words - full_words
        
        if unique_partial_words:
            # Intentar incorporar información única de la dirección parcial
            street_number_match = re.search(r'\d+', partial_address)
            if street_number_match and not re.search(r'\d+', full_address):
                return f"{street_number_match.group()} {full_address}"
        
        return full_address
    
    def enrich_location_data(self, address_data: Dict, coordinates: Tuple[float, float] = None, 
                           clean_special_chars: bool = False, aggressive: bool = False) -> Dict:
        """
        Añade información adicional a los datos de ubicación
        
        Args:
            address_data (Dict): Datos de dirección existentes
            coordinates (Tuple[float, float]): Coordenadas opcionales
            clean_special_chars (bool): Si True, limpia caracteres especiales de las direcciones
            aggressive (bool): Si True, usa limpieza agresiva (también elimina caracteres acentuados)
        
        Returns:
            Dict: Datos enriquecidos
        """
        enriched = address_data.copy()
        
        try:
            lat, lng = coordinates if coordinates else (None, None)
            
            # Si no tenemos coordenadas, intentar obtenerlas de la dirección
            if not coordinates and address_data.get('address'):
                geocode_result = self.geocoder.geocode(address_data['address'])
                if geocode_result:
                    lat = geocode_result[0]['geometry']['lat']
                    lng = geocode_result[0]['geometry']['lng']
                    enriched['coordinates'] = {'lat': lat, 'lng': lng}
            
            # Obtener información detallada del lugar
            if lat and lng:
                # Añadir parámetros para controlar formato de respuesta
                params = {}
                if clean_special_chars:
                    params['no_annotations'] = 1
                
                reverse_result = self.geocoder.reverse_geocode(lat, lng, **params)
                if reverse_result:
                    components = reverse_result[0].get('components', {})
                    annotations = reverse_result[0].get('annotations', {})
                    
                    # Limpiar componentes si se solicita
                    if clean_special_chars:
                        for key, value in components.items():
                            if isinstance(value, str):
                                components[key] = clean_address_text(value, aggressive)
                    
                    # Información de zona horaria
                    timezone_info = annotations.get('timezone', {})
                    enriched['timezone'] = {
                        'name': timezone_info.get('name', ''),
                        'offset_sec': timezone_info.get('offset_sec', 0),
                        'offset_string': timezone_info.get('offset_string', '')
                    }
                    
                    # Jerarquía administrativa
                    enriched['administrative_levels'] = {
                        'country': components.get('country', ''),
                        'country_code': components.get('country_code', ''),
                        'state': components.get('state', ''),
                        'state_code': components.get('state_code', ''),
                        'province': components.get('province', ''),
                        'county': components.get('county', ''),
                        'city': components.get('city', ''),
                        'town': components.get('town', ''),
                        'village': components.get('village', ''),
                        'suburb': components.get('suburb', ''),
                        'neighbourhood': components.get('neighbourhood', '')
                    }
                    
                    # Información postal y geográfica
                    enriched['geographic_info'] = {
                        'postcode': components.get('postcode', ''),
                        'continent': annotations.get('continent', ''),
                        'currency': annotations.get('currency', {}),
                        'calling_code': annotations.get('callingcode', ''),
                        'flag': annotations.get('flag', ''),
                        'geohash': annotations.get('geohash', ''),
                        'what3words': annotations.get('what3words', {})
                    }
                    
                    # Información de formato y calidad
                    enriched['quality_info'] = {
                        'mgrs': annotations.get('MGRS', ''),
                        'maidenhead': annotations.get('Maidenhead', ''),
                        'mercator': annotations.get('Mercator', {}),
                        'osm': annotations.get('OSM', {}),
                        'un_m49': annotations.get('UN_M49', {})
                    }
                    
                    # Información meteorológica si está disponible
                    if 'DMS' in annotations:
                        enriched['coordinate_systems'] = {
                            'dms': annotations['DMS'],
                            'mgrs': annotations.get('MGRS', ''),
                            'maidenhead': annotations.get('Maidenhead', '')
                        }
            
            # Añadir timestamp del enriquecimiento
            enriched['enrichment_timestamp'] = datetime.now().isoformat()
            enriched['enrichment_version'] = '1.0'
            
        except Exception as e:
            enriched['enrichment_error'] = str(e)
        
        return enriched
    
    def validate_postal_code(self, postal_code: str, country_code: str = None) -> Dict[str, Union[bool, str]]:
        """
        Valida códigos postales contra patrones conocidos
        
        Args:
            postal_code (str): Código postal a validar
            country_code (str): Código de país opcional
        
        Returns:
            Dict: Resultado de validación
        """
        if not postal_code:
            return {'is_valid': False, 'reason': 'empty_postal_code'}
        
        # Patrones de códigos postales por país
        postal_patterns = {
            'ES': r'^\d{5}$',  # España: 5 dígitos
            'US': r'^\d{5}(-\d{4})?$',  # Estados Unidos: 5 dígitos o 5+4
            'CA': r'^[A-Z]\d[A-Z]\s?\d[A-Z]\d$',  # Canadá: A1A 1A1
            'MX': r'^\d{5}$',  # México: 5 dígitos
            'GB': r'^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$',  # Reino Unido
            'FR': r'^\d{5}$',  # Francia: 5 dígitos
            'DE': r'^\d{5}$',  # Alemania: 5 dígitos
            'IT': r'^\d{5}$',  # Italia: 5 dígitos
            'BR': r'^\d{5}-?\d{3}$',  # Brasil: 12345-678
            'AR': r'^[A-Z]?\d{4}[A-Z]{3}$|^\d{4}$',  # Argentina
            'CO': r'^\d{6}$',  # Colombia: 6 dígitos
        }
        
        postal_code_clean = postal_code.strip().upper()
        
        # Si tenemos código de país, usar patrón específico
        if country_code and country_code.upper() in postal_patterns:
            pattern = postal_patterns[country_code.upper()]
            is_valid = bool(re.match(pattern, postal_code_clean))
            return {
                'is_valid': is_valid,
                'country_code': country_code.upper(),
                'pattern_used': pattern,
                'cleaned_postal_code': postal_code_clean
            }
        
        # Si no tenemos país, intentar con todos los patrones
        for country, pattern in postal_patterns.items():
            if re.match(pattern, postal_code_clean):
                return {
                    'is_valid': True,
                    'possible_country': country,
                    'pattern_matched': pattern,
                    'cleaned_postal_code': postal_code_clean
                }
        
        return {
            'is_valid': False,
            'reason': 'no_pattern_match',
            'cleaned_postal_code': postal_code_clean
        }
    
    def process_address_batch(self, addresses: List[Dict], delay: float = 1.0, 
                            language: str = 'es', clean_special_chars: bool = False, 
                            aggressive: bool = False) -> List[Dict]:
        """
        Procesa un lote de direcciones para limpiar, validar y enriquecer
        
        Args:
            addresses (List[Dict]): Lista de direcciones a procesar
            delay (float): Retraso entre solicitudes de API
            language (str): Idioma para resultados
            clean_special_chars (bool): Si True, limpia caracteres especiales de las direcciones
            aggressive (bool): Si True, usa limpieza agresiva (también elimina caracteres acentuados)
        
        Returns:
            List[Dict]: Direcciones procesadas y enriquecidas
        """
        processed_addresses = []
        
        for i, addr_data in enumerate(addresses):
            print(f"Procesando dirección {i+1}/{len(addresses)}")
            
            try:
                # Extraer información de la dirección
                address = addr_data.get('address', '')
                coordinates = None
                if 'lat' in addr_data and 'lng' in addr_data:
                    coordinates = (float(addr_data['lat']), float(addr_data['lng']))
                
                # Paso 1: Detectar si la dirección está incompleta
                completeness = self.detect_incomplete_address(address)
                
                # Paso 2: Completar dirección si es necesario
                if not completeness['is_complete'] or completeness['confidence'] < 0.7:
                    completion_result = self.complete_address(
                        address, coordinates, language, clean_special_chars, aggressive
                    )
                    addr_data.update(completion_result)
                
                # Paso 3: Normalizar formato
                if addr_data.get('completed_address'):
                    addr_data['normalized_address'] = self.normalize_address_format(
                        addr_data['completed_address'], language
                    )
                
                # Paso 4: Validar código postal si existe
                if 'postcode' in addr_data.get('components', {}):
                    postal_validation = self.validate_postal_code(
                        addr_data['components']['postcode'],
                        addr_data['components'].get('country_code')
                    )
                    addr_data['postal_validation'] = postal_validation
                
                # Paso 5: Enriquecer con datos adicionales
                final_coords = coordinates
                if not final_coords and addr_data.get('coordinates'):
                    final_coords = (addr_data['coordinates']['lat'], addr_data['coordinates']['lng'])
                
                enriched_data = self.enrich_location_data(
                    addr_data, final_coords, clean_special_chars, aggressive
                )
                addr_data.update(enriched_data)
                
                # Añadir métricas de calidad
                addr_data['quality_metrics'] = {
                    'completeness_score': completeness['confidence'],
                    'has_coordinates': final_coords is not None,
                    'method_used': addr_data.get('method_used', 'none'),
                    'processing_timestamp': datetime.now().isoformat()
                }
                
                processed_addresses.append(addr_data)
                
                # Respetar límites de la API
                if i < len(addresses) - 1:
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"Error procesando dirección {i+1}: {e}")
                addr_data['processing_error'] = str(e)
                processed_addresses.append(addr_data)
        
        return processed_addresses
    
    def export_enhanced_addresses(self, addresses: List[Dict], output_file: str, 
                                format_type: str = 'csv'):
        """
        Exporta direcciones enriquecidas a archivo
        
        Args:
            addresses (List[Dict]): Direcciones procesadas
            output_file (str): Archivo de salida
            format_type (str): Formato ('csv' o 'json')
        """
        try:
            if format_type.lower() == 'csv':
                # Aplanar datos complejos para CSV
                flattened_addresses = []
                for addr in addresses:
                    flat_addr = {}
                    for key, value in addr.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                flat_addr[f"{key}_{sub_key}"] = sub_value
                        else:
                            flat_addr[key] = value
                    flattened_addresses.append(flat_addr)
                
                if flattened_addresses:
                    df = pd.DataFrame(flattened_addresses)
                    df.to_csv(output_file, index=False, encoding='utf-8')
                    print(f"Direcciones enriquecidas exportadas a {output_file}")
            
            elif format_type.lower() == 'json':
                import json
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(addresses, f, indent=2, ensure_ascii=False)
                print(f"Direcciones enriquecidas exportadas a {output_file}")
            
        except Exception as e:
            print(f"Error exportando direcciones: {e}")


def main():
    """
    Función principal para demostrar el uso del AddressEnhancer
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Limpieza y Enriquecimiento de Direcciones')
    parser.add_argument('input_file', help='Archivo CSV con direcciones a procesar')
    parser.add_argument('-o', '--output', default='enhanced_addresses.csv', 
                       help='Archivo de salida (default: enhanced_addresses.csv)')
    parser.add_argument('--language', default='es', help='Idioma para resultados (default: es)')
    parser.add_argument('--delay', type=float, default=1.0, 
                       help='Retraso entre solicitudes API en segundos (default: 1.0)')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv',
                       help='Formato de salida (default: csv)')
    parser.add_argument('--clean', action='store_true',
                       help='Limpiar caracteres especiales de las direcciones (elimina ?, !, @, etc.)')
    parser.add_argument('--aggressive', action='store_true',
                       help='Usar limpieza agresiva (también elimina caracteres acentuados para compatibilidad)')
    
    args = parser.parse_args()
    
    try:
        # Inicializar el enhancer
        enhancer = AddressEnhancer()
        
        # Cargar direcciones desde archivo
        print(f"Cargando direcciones desde {args.input_file}...")
        df = pd.read_csv(args.input_file)
        addresses = df.to_dict('records')
        
        print(f"Encontradas {len(addresses)} direcciones para procesar")
        
        # Mostrar configuración de limpieza
        if args.clean:
            print(f"🧽 Limpieza de caracteres especiales: {'Agresiva' if args.aggressive else 'Conservadora'}")
        
        # Procesar direcciones
        enhanced_addresses = enhancer.process_address_batch(
            addresses, 
            delay=args.delay, 
            language=args.language,
            clean_special_chars=args.clean,
            aggressive=args.aggressive
        )
        
        # Exportar resultados
        enhancer.export_enhanced_addresses(
            enhanced_addresses, 
            args.output, 
            args.format
        )
        
        print(f"\n✓ Procesamiento completado!")
        print(f"Direcciones procesadas: {len(enhanced_addresses)}")
        print(f"Resultados guardados en: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
