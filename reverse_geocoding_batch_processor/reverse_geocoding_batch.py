#!/usr/bin/env python3
"""
Batch Reverse Geocoding Script
Reads coordinates from CSV/TXT files and performs reverse geocoding using OpenCage API
"""

import csv
import pandas as pd
import os
import sys
from dotenv import load_dotenv
from opencage.geocoder import OpenCageGeocode
import time
from typing import List, Tuple, Dict, Optional
import argparse

'''
Clean address text by removing special characters and extra whitespace.
@param text: The address text to clean.
@param aggressive: If True, removes some accented characters for compatibility.
@return: Cleaned address text.
'''
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
    
    import re
    
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

'''
Load environment variables and get API key
@param: None
@return: API key as string
@raises: ValueError if OPENCAGE_API_KEY is not found
'''
def load_dotenv_and_get_key() -> str:
    """Load environment variables and get API key"""
    load_dotenv()
    key = os.getenv('OPENCAGE_API_KEY')
    if not key:
        raise ValueError("OPENCAGE_API_KEY not found in environment variables or .env file")
    return key

'''
Read coordinates from CSV file
Assumes the CSV has columns named 'lat' and 'lng' or similar variations
Returns a list of (latitude, longitude) tuples
@param file_path: Path to the CSV file
@return: List of (latitude, longitude) tuples
'''
def read_coordinates_from_csv(file_path: str) -> List[Tuple[float, float]]:
    """Read coordinates from CSV file"""
    try:
        df = pd.read_csv(file_path)
        
        # Try to identify latitude and longitude columns
        lat_col = None
        lng_col = None
        
        # Common column names
        possible_lat_names = ['lat', 'latitude', 'Lat', 'Latitude', 'LAT', 'LATITUDE']
        possible_lng_names = ['lng', 'longitude', 'Lng', 'Longitude', 'LNG', 'LONGITUDE', 'lon']
        
        for col in df.columns:
            col_clean = col.strip().lower()
            if col_clean in [name.lower() for name in possible_lat_names]:
                lat_col = col
            elif col_clean in [name.lower() for name in possible_lng_names]:
                lng_col = col
        
        if lat_col is None or lng_col is None:
            # If we can't find standard column names, assume first two columns
            if len(df.columns) >= 2:
                lat_col = df.columns[0]
                lng_col = df.columns[1]
            else:
                raise ValueError("Could not identify latitude and longitude columns")
        
        coordinates = []
        for idx, row in df.iterrows():
            try:
                lat = float(row[lat_col])
                lng = float(row[lng_col])
                coordinates.append((lat, lng))
            except (ValueError, TypeError) as e:
                print(f"Warning: Skipping row {idx + 1}, invalid coordinates: {row[lat_col]}, {row[lng_col]}")
                continue
        
        return coordinates
    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

'''
Read coordinates from TXT file (format: lat,lng or lat lng)
@param file_path: Path to the TXT file
@return: List of (latitude, longitude) tuples
'''
def read_coordinates_from_txt(file_path: str) -> List[Tuple[float, float]]:
    """Read coordinates from TXT file (format: lat,lng or lat lng)"""
    coordinates = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue
                
                try:
                    # Try comma-separated first
                    if ',' in line:
                        parts = line.split(',')
                    else:
                        # Try space-separated
                        parts = line.split()
                    
                    if len(parts) >= 2:
                        lat = float(parts[0].strip())
                        lng = float(parts[1].strip())
                        coordinates.append((lat, lng))
                    else:
                        print(f"Warning: Skipping line {line_num}, insufficient data: {line}")
                        
                except (ValueError, IndexError) as e:
                    print(f"Warning: Skipping line {line_num}, invalid format: {line}")
                    continue
    
    except Exception as e:
        print(f"Error reading TXT file: {e}")
        return []
    
    return coordinates

'''
Reverse geocode a list of coordinates
@param geocoder: OpenCageGeocode instance
@param coordinates: List of (latitude, longitude) tuples
@param delay: Delay between API requests in seconds
@param clean_special_chars: If True, clean special characters from addresses
@param aggressive: If True, use aggressive cleaning (removes some accented characters)
@param language: Language for geocoding results (e.g., 'es', 'en', 'fr', 'de')
@param country_code: Country code to bias results (e.g., 'es', 'us')
@return: List of dictionaries with geocoding results
'''
def reverse_geocode_coordinates(geocoder: OpenCageGeocode, coordinates: List[Tuple[float, float]], 
                              delay: float = 1.0, clean_special_chars: bool = False, aggressive: bool = False,
                              language: str = 'en', country_code: Optional[str] = None) -> List[Dict]:
    """Perform reverse geocoding for a list of coordinates"""
    results = []
    
    for i, (lat, lng) in enumerate(coordinates):
        try:
            print(f"Processing coordinate {i+1}/{len(coordinates)}: ({lat}, {lng})")
            
            # Add parameters to control response format
            params = {}
            if clean_special_chars:
                # Use no_annotations=1 to get cleaner results without special characters
                params['no_annotations'] = 1
            
            # Add language parameter
            if language and language != 'en':
                params['language'] = language
            
            # Add country bias parameter
            if country_code:
                params['countrycode'] = country_code
            
            result = geocoder.reverse_geocode(lat, lng, **params)
            
            if result:
                address = result[0]['formatted']
                
                # Clean special characters if requested
                if clean_special_chars:
                    address = clean_address_text(address, aggressive)
                
                # Extract additional information if available
                components = result[0].get('components', {})
                country = components.get('country', '')
                state = components.get('state', '')
                city = components.get('city', '')
                postcode = components.get('postcode', '')
                
                # Clean component fields if requested
                if clean_special_chars:
                    country = clean_address_text(country, aggressive)
                    state = clean_address_text(state, aggressive)
                    city = clean_address_text(city, aggressive)
                
                results.append({
                    'latitude': lat,
                    'longitude': lng,
                    'address': address,
                    'country': country,
                    'state': state,
                    'city': city,
                    'postcode': postcode
                })
            else:
                results.append({
                    'latitude': lat,
                    'longitude': lng,
                    'address': 'No result found',
                    'country': '',
                    'state': '',
                    'city': '',
                    'postcode': ''
                })
            
            # Add delay to respect API rate limits
            if i < len(coordinates) - 1:  # Don't delay after the last request
                time.sleep(delay)
                
        except Exception as e:
            print(f"Error processing coordinate ({lat}, {lng}): {e}")
            results.append({
                'latitude': lat,
                'longitude': lng,
                'address': f'Error: {str(e)}',
                'country': '',
                'state': '',
                'city': '',
                'postcode': ''
            })
    
    return results

'''
Save results to CSV file
@param results: List of dictionaries with geocoding results
@param output_file: Path to the output CSV file
@return: None
'''
def save_results_to_csv(results: List[Dict], output_file: str):
    """Save results to CSV file"""
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if results:
                fieldnames = results[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        
        print(f"Results saved to {output_file}")
        print(f"Total coordinates processed: {len(results)}")
        
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    parser = argparse.ArgumentParser(description='Batch Reverse Geocoding with OpenCage API')
    parser.add_argument('input_file', help='Input CSV or TXT file with coordinates')
    parser.add_argument('-o', '--output', help='Output CSV file (default: results.csv)')
    parser.add_argument('-d', '--delay', type=float, default=1.0, 
                       help='Delay between API requests in seconds (default: 1.0)')
    parser.add_argument('--format', choices=['csv', 'txt'], 
                       help='Input file format (auto-detected if not specified)')
    parser.add_argument('--clean', action='store_true',
                       help='Clean special characters from addresses (remove ?, !, @, etc.)')
    parser.add_argument('--aggressive', action='store_true',
                       help='Use aggressive cleaning (also removes accented characters for compatibility)')
    parser.add_argument('--language', default='en',
                       help='Language for geocoding results (e.g., es, en, fr, de)')
    parser.add_argument('--country-code', default=None,
                       help='Country code to bias results (e.g., es, us, fr)')
    
    args = parser.parse_args()
    
    # Determine output file
    output_file = args.output or 'results.csv'
    
    # Determine input format
    if args.format:
        input_format = args.format
    else:
        input_format = 'csv' if args.input_file.lower().endswith('.csv') else 'txt'
    
    try:
        # Load API key
        api_key = load_dotenv_and_get_key()
        geocoder = OpenCageGeocode(api_key)
        
        # Read coordinates
        print(f"Reading coordinates from {args.input_file}...")
        if input_format == 'csv':
            coordinates = read_coordinates_from_csv(args.input_file)
        else:
            coordinates = read_coordinates_from_txt(args.input_file)
        
        if not coordinates:
            print("No valid coordinates found in input file")
            return
        
        print(f"Found {len(coordinates)} coordinates to process")
        
        # Perform reverse geocoding
        print("Starting reverse geocoding...")
        print(f"Language: {args.language}")
        if args.country_code:
            print(f"Country bias: {args.country_code}")
        results = reverse_geocode_coordinates(geocoder, coordinates, args.delay, args.clean, args.aggressive, args.language, args.country_code)
        
        # Save results
        save_results_to_csv(results, output_file)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
