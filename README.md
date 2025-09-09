# Reverse Geocoding Project 🌍

Un sistema completo de geocodificación y enriquecimiento de datos de direcciones usando la API de OpenCage.

## 🚀 Funcionalidades

### ✨ Nuevas Funcionalidades de Limpieza y Enriquecimiento
- **Sistema de Completado Inteligente**: Completa direcciones parciales usando coordenadas o geocodificación
- **Validador y Normalizador**: Detecta errores, normaliza formatos y valida códigos postales
- **Enriquecimiento Geográfico**: Añade información de zona horaria, jerarquía administrativa, y datos demográficos

### 🔄 Funcionalidades Originales
- **Geocodificación directa**: Convierte direcciones en coordenadas
- **Geocodificación inversa**: Convierte coordenadas en direcciones
- **Procesamiento en lote**: Procesa múltiples ubicaciones desde archivos CSV/TXT

## 📁 Estructura del Proyecto

```
reverse_geocoding/
├── README.md                                    # Documentación principal
├── README_enhanced.md                           # 🆕 Documentación completa del sistema enriquecido
├── reverse_geocoding.ipynb                      # Notebook original de geocodificación
├── address_enhancement_demo.ipynb               # 🆕 Demo interactiva del sistema de enriquecimiento
├── integration_demo.py                          # 🆕 Script de demostración de integración
└── reverse_geocoding_batch_processor/
    ├── install_dependencies.py                  # Instalador de dependencias
    ├── reverse_geocoding_batch.py               # Script de procesamiento en lote
    ├── address_enhancer.py                      # 🆕 Sistema de limpieza y enriquecimiento
    ├── Prueba_OpenCAge.csv                     # Archivo de prueba
    └── results.csv                             # Resultados de ejemplo
```

## ⚡ Inicio Rápido

### 1. Configuración Inicial
```bash
# Instalar dependencias
python reverse_geocoding_batch_processor/install_dependencies.py

# Crear archivo .env con tu API key
echo "OPENCAGE_API_KEY=tu_api_key_aqui" > .env
```

### 2. Probar el Sistema Completo
```bash
# Ejecutar demostración completa
python integration_demo.py

# O abrir el notebook interactivo
jupyter notebook address_enhancement_demo.ipynb
```

### 3. Procesar tus Datos
```bash
# Sistema original (geocodificación reversa)
python reverse_geocoding_batch_processor/reverse_geocoding_batch.py coordenadas.csv

# Sistema enriquecido (limpieza y enriquecimiento)
python reverse_geocoding_batch_processor/address_enhancer.py direcciones.csv -o direcciones_enriquecidas.csv
```

## 🎯 Ejemplos de Uso

### Completado Inteligente de Direcciones
```python
from reverse_geocoding_batch_processor.address_enhancer import AddressEnhancer

enhancer = AddressEnhancer()

# Completar usando coordenadas
result = enhancer.complete_address(
    "Gran Vía 25", 
    coordinates=(40.4200, -3.7025)
)
print(result['completed_address'])
# → "Gran Vía 25, Centro, Madrid, Comunidad de Madrid, 28013, España"
```

### Normalización y Validación
```python
# Normalizar formato
normalized = enhancer.normalize_address_format("c/ mayor 15", 'es')
print(normalized)  # → "Calle Mayor 15"

# Validar código postal
validation = enhancer.validate_postal_code("28013", "ES")
print(validation['is_valid'])  # → True
```

### Enriquecimiento Completo
```python
# Enriquecer con datos geográficos
enriched = enhancer.enrich_location_data({
    'address': 'Puerta del Sol, Madrid'
})

print(f"Zona horaria: {enriched['timezone']['name']}")
print(f"Moneda: {enriched['geographic_info']['currency']['name']}")
print(f"Continente: {enriched['geographic_info']['continent']}")
```

## 📊 Comparación de Capacidades

| Funcionalidad | Sistema Original | Sistema Enriquecido |
|---------------|------------------|-------------------|
| Geocodificación directa | ✅ | ✅ |
| Geocodificación inversa | ✅ | ✅ |
| Procesamiento en lote | ✅ | ✅ |
| Limpieza de direcciones | ❌ | ✅ |
| Detección de errores | ❌ | ✅ |
| Normalización de formatos | ❌ | ✅ |
| Validación de códigos postales | ❌ | ✅ |
| Completado inteligente | ❌ | ✅ |
| Enriquecimiento geográfico | ❌ | ✅ |
| Información de zona horaria | ❌ | ✅ |
| Datos demográficos | ❌ | ✅ |

## 🔧 Configuración Avanzada

Para configuración detallada, casos de uso específicos y documentación completa de la API, consulta **[README_enhanced.md](README_enhanced.md)**.

## 📚 Recursos Adicionales

- **[Demo Interactiva](address_enhancement_demo.ipynb)**: Jupyter notebook con ejemplos paso a paso
- **[Script de Integración](integration_demo.py)**: Demostración de todas las funcionalidades
- **[Documentación Completa](README_enhanced.md)**: Guía detallada del sistema enriquecido
- **[Especificaciones](reverse_geocoding_batch_processor/rules.md)**: Reglas de implementación

## 🤝 Integración

El sistema enriquecido es **100% compatible** con las herramientas existentes:
- ✅ Mismas dependencias
- ✅ Misma configuración de API
- ✅ Formatos de datos compatibles
- ✅ Sin cambios en código existente

¡Puedes empezar a usar las nuevas funcionalidades inmediatamente!

---

# Documentación Original: Mejoras para la Herramienta

Basándome en tu implementación actual con la API de OpenCage, veo que tienes una herramienta funcional de geocodificación reversa. Aquí te propongo varias mejoras que puedes implementar para hacer tu herramienta más robusta y completa:

## Mejoras Técnicas

### 1. **Manejo de Errores y Límites de API**
```python
import time
import logging
from opencage.geocoder import RateLimitExceededError, InvalidInputError

def reverse_geocode_with_retry(geocoder, lat, lng, max_retries=3):
    for attempt in range(max_retries):
        try:
            results = geocoder.reverse_geocode(lat, lng)
            return results
        except RateLimitExceededError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Backoff exponencial
                continue
            raise
        except Exception as e:
            logging.error(f"Error en intento {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
```

### 2. **Extracción de Componentes Específicos**
Aprovecha la respuesta detallada de OpenCage para extraer componentes específicos:

```python
def extract_address_components(result):
    components = result.get('components', {})
    return {
        'street': components.get('road', ''),
        'house_number': components.get('house_number', ''),
        'neighborhood': components.get('neighbourhood', ''),
        'city': components.get('city', components.get('town', components.get('village', ''))),
        'state': components.get('state', ''),
        'postal_code': components.get('postcode', ''),
        'country': components.get('country', ''),
        'country_code': components.get('country_code', ''),
        'formatted': result.get('formatted', '')
    }
```

### 3. **Configuración de Parámetros Avanzados**
```python
def enhanced_reverse_geocode(geocoder, lat, lng, language='es', no_annotations=0):
    results = geocoder.reverse_geocode(
        lat, lng,
        language=language,
        no_annotations=no_annotations,
        roadinfo=1,
        no_dedupe=1
    )
    return results
```

### 4. **Procesamiento en Lotes Optimizado**
```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

async def process_coordinates_batch(coordinates_list, api_key, batch_size=50):
    semaphore = asyncio.Semaphore(10)  # Límite de concurrencia
    
    async def process_single_coordinate(lat, lng):
        async with semaphore:
            # Implementar llamada asíncrona a la API
            pass
    
    tasks = []
    for lat, lng in coordinates_list:
        task = asyncio.create_task(process_single_coordinate(lat, lng))
        tasks.append(task)
    
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### 5. **Caché Local para Optimizar Consultas**
```python
import sqlite3
import hashlib

class GeocodingCache:
    def __init__(self, db_path='geocoding_cache.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_table()
    
    def create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS geocoding_cache (
                coord_hash TEXT PRIMARY KEY,
                latitude REAL,
                longitude REAL,
                address TEXT,
                components TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def get_cached_result(self, lat, lng, precision=4):
        rounded_lat = round(lat, precision)
        rounded_lng = round(lng, precision)
        coord_hash = hashlib.md5(f"{rounded_lat},{rounded_lng}".encode()).hexdigest()
        
        cursor = self.conn.execute(
            'SELECT address, components FROM geocoding_cache WHERE coord_hash = ?',
            (coord_hash,)
        )
        return cursor.fetchone()
```

### 6. **Validación y Normalización de Coordenadas**
```python
def validate_coordinates(lat, lng):
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitud inválida: {lat}. Debe estar entre -90 y 90.")
    if not (-180 <= lng <= 180):
        raise ValueError(f"Longitud inválida: {lng}. Debe estar entre -180 y 180.")
    
    # Normalizar precision
    return round(lat, 6), round(lng, 6)
```

### 7. **Configuración Específica por Región**
```python
def get_region_specific_config(country_code):
    configs = {
        'ES': {'language': 'es', 'country_code': 'es'},
        'PE': {'language': 'es', 'country_code': 'pe'},
        'MX': {'language': 'es', 'country_code': 'mx'},
        'US': {'language': 'en', 'country_code': 'us'},
    }
    return configs.get(country_code.upper(), {'language': 'en'})
```

### 8. **Métricas y Monitoreo**
```python
class GeocodingMetrics:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.cache_hits = 0
        self.api_calls = 0
    
    def log_request(self, success=True, from_cache=False):
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        if from_cache:
            self.cache_hits += 1
        else:
            self.api_calls += 1
```

## Funcionalidades Adicionales con OpenCage

### 9. **Detección de Confianza y Calidad**
```python
def assess_result_quality(result):
    confidence = result.get('confidence', 0)
    quality_score = {
        'confidence': confidence,
        'has_house_number': bool(result.get('components', {}).get('house_number')),
        'has_road': bool(result.get('components', {}).get('road')),
        'precision': 'high' if confidence >= 7 else 'medium' if confidence >= 4 else 'low'
    }
    return quality_score
```

### 10. **Filtrado por Tipo de Lugar**
```python
def filter_by_place_type(results, preferred_types=['building', 'address', 'street']):
    filtered_results = []
    for result in results:
        components = result.get('components', {})
        result_type = components.get('_type', '')
        if result_type in preferred_types:
            filtered_results.append(result)
    return filtered_results or results  # Fallback a resultados originales
```

Estas mejoras te permitirán:
- **Mejor rendimiento** con caché y procesamiento asíncrono
- **Mayor precisión** con validación y filtrado de resultados
- **Robustez** con manejo de errores y reintentos
- **Flexibilidad** con configuraciones específicas por región
- **Monitoreo** del uso y rendimiento de la herramienta
