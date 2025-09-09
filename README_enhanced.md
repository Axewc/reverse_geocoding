# Sistema de Limpieza y Enriquecimiento de Direcciones

Un sistema completo para limpiar, validar, completar y enriquecer datos de direcciones, integrado con la API de OpenCage Geocoding.

## 🚀 Nuevas Funcionalidades

### 1. Sistema de Completado Inteligente de Direcciones
- **Completado usando coordenadas**: Utiliza geocodificación inversa para completar direcciones parciales
- **Completado usando geocodificación directa**: Mejora direcciones incompletas obteniendo información adicional
- **Fusión inteligente de datos**: Combina información de múltiples fuentes para obtener direcciones más precisas

### 2. Validador y Normalizador de Direcciones
- **Detección de direcciones incompletas**: Identifica qué componentes faltan en una dirección
- **Normalización de formatos**: Estandariza abreviaciones (Calle → C/, Street → St., etc.)
- **Corrección de errores**: Sugiere correcciones para errores comunes de tipeo
- **Validación de códigos postales**: Valida códigos postales contra patrones conocidos por país

### 3. Sistema de Enriquecimiento de Datos Geográficos
- **Información de zona horaria**: Añade datos de zona horaria y offset UTC
- **Jerarquía administrativa**: Extrae información completa de país, estado, ciudad, barrio, etc.
- **Datos demográficos y geográficos**: Incluye información de continente, moneda, código telefónico
- **Sistemas de coordenadas**: Proporciona coordenadas en diferentes formatos (DMS, MGRS, Maidenhead)
- **Contexto geográfico**: Información adicional como geohash, what3words, etc.

## 📁 Estructura del Proyecto

```
reverse_geocoding/
├── README.md                                    # Este archivo
├── reverse_geocoding.ipynb                      # Notebook original de geocodificación
├── address_enhancement_demo.ipynb               # 🆕 Demo del sistema de enriquecimiento
└── reverse_geocoding_batch_processor/
    ├── install_dependencies.py                  # Instalador de dependencias actualizado
    ├── reverse_geocoding_batch.py               # Script original de procesamiento en lote
    ├── address_enhancer.py                      # 🆕 Sistema de limpieza y enriquecimiento
    ├── Prueba_OpenCAge.csv                     # Archivo de prueba
    ├── results.csv                             # Resultados de ejemplo
    └── README.md                               # Documentación del batch processor
```

## ⚙️ Instalación y Configuración

### 1. Instalar Dependencias

```bash
# Opción 1: Usar el script automático
python reverse_geocoding_batch_processor/install_dependencies.py

# Opción 2: Instalación manual
pip install python-dotenv opencage pandas requests
```

### 2. Configurar API Key

Crea un archivo `.env` en el directorio raíz del proyecto:

```env
OPENCAGE_API_KEY=tu_api_key_aqui
```

## 🎯 Uso del Sistema

### Desde Jupyter Notebook (Recomendado para exploración)

Abre `address_enhancement_demo.ipynb` para ver ejemplos interactivos de todas las funcionalidades.

### Desde Línea de Comandos

```bash
# Procesar archivo CSV con direcciones (básico)
python reverse_geocoding_batch_processor/address_enhancer.py input_addresses.csv -o enhanced_output.csv

# 🆕 Con limpieza de caracteres especiales (conservadora)
python reverse_geocoding_batch_processor/address_enhancer.py input_addresses.csv -o enhanced_output.csv --clean

# 🆕 Con limpieza agresiva (elimina también acentos)
python reverse_geocoding_batch_processor/address_enhancer.py input_addresses.csv -o enhanced_output.csv --clean --aggressive

# Opciones completas
python reverse_geocoding_batch_processor/address_enhancer.py input_addresses.csv \
    --output enhanced_addresses.csv \
    --language es \
    --delay 1.0 \
    --format csv \
    --clean \
    --aggressive
```

### Uso Programático

```python
from reverse_geocoding_batch_processor.address_enhancer import AddressEnhancer

# Inicializar
enhancer = AddressEnhancer()

# Detectar direcciones incompletas
analysis = enhancer.detect_incomplete_address("Calle 123")
print(f"Completa: {analysis['is_complete']}")
print(f"Confianza: {analysis['confidence']}")

# Completar dirección
result = enhancer.complete_address(
    partial_address="Gran Vía, Madrid",
    coordinates=(40.4200, -3.7025),  # Opcional
    language='es'
)
print(f"Completada: {result['completed_address']}")

# 🆕 Completar dirección CON limpieza de caracteres especiales
result_clean = enhancer.complete_address(
    partial_address="Gran Vía!!! @Madrid",
    coordinates=(40.4200, -3.7025),
    language='es',
    clean_special_chars=True,    # Activar limpieza
    aggressive=False             # Limpieza conservadora (mantiene acentos)
)
print(f"Completada y limpia: {result_clean['completed_address']}")

# Normalizar formato
normalized = enhancer.normalize_address_format("c/ mayor 25", target_language='es')
print(f"Normalizada: {normalized}")  # "Calle Mayor 25"

# Validar código postal
validation = enhancer.validate_postal_code("28013", "ES")
print(f"Válido: {validation['is_valid']}")

# Enriquecer con datos geográficos
enriched = enhancer.enrich_location_data({
    'address': 'Puerta del Sol, Madrid'
})
print(f"Zona horaria: {enriched['timezone']['name']}")

# 🆕 Procesar en lote CON limpieza
addresses = [
    {'address': 'Gran Vía 25!!! @Madrid'},
    {'address': 'Sagrada Família', 'lat': 41.4036, 'lng': 2.1744}
]
enhanced = enhancer.process_address_batch(
    addresses, 
    delay=1.0, 
    language='es',
    clean_special_chars=True,    # 🆕 Activar limpieza
    aggressive=False             # 🆕 Limpieza conservadora
)
```

## 📊 Formato de Entrada

### CSV de Entrada (Mínimo)
```csv
address
"Gran Vía 25"
"Sagrada Familia, Barcelona"
"c/ mayor 15, madrid"
```

### CSV de Entrada (Completo)
```csv
address,lat,lng,city,country
"Gran Vía 25",40.4200,-3.7025,"Madrid","España"
"Sagrada Familia",,,"Barcelona","España"
"Times Square",,,"New York","USA"
```

## 📈 Formato de Salida

El sistema genera archivos CSV enriquecidos con las siguientes columnas principales:

### Datos Básicos
- `original_address`: Dirección original
- `completed_address`: Dirección completada
- `normalized_address`: Dirección normalizada
- `method_used`: Método usado para completar

### Coordenadas
- `coordinates_lat`: Latitud
- `coordinates_lng`: Longitud

### Componentes de Dirección
- `components_country`: País
- `components_state`: Estado/Provincia
- `components_city`: Ciudad
- `components_postcode`: Código postal

### Información Geográfica
- `timezone_name`: Zona horaria
- `timezone_offset_string`: Offset UTC
- `geographic_info_continent`: Continente
- `geographic_info_currency_name`: Moneda
- `geographic_info_calling_code`: Código telefónico

### Métricas de Calidad
- `quality_metrics_completeness_score`: Puntuación de completitud (0-1)
- `quality_metrics_has_coordinates`: Tiene coordenadas (true/false)
- `quality_metrics_method_used`: Método de procesamiento
- `quality_metrics_processing_timestamp`: Timestamp del procesamiento

## 🔧 Configuración Avanzada

### 🆕 Opciones de Limpieza de Caracteres Especiales

El sistema incluye funcionalidad integrada del sistema original para limpiar caracteres especiales en direcciones:

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `clean_special_chars=False` | Sin limpieza (por defecto) | `"Calle Mayor!!! @Madrid"` → Sin cambios |
| `clean_special_chars=True, aggressive=False` | Limpieza conservadora | `"Calle Mayor!!! @Madrid"` → `"Calle Mayor Madrid"` |
| `clean_special_chars=True, aggressive=True` | Limpieza agresiva | `"Calle Alcalá!!! @Madrid"` → `"Calle Alcala Madrid"` |

#### Caracteres que se eliminan:
- **Conservadora**: `? ¿ ! ¡ @ # $ % ^ & * ( ) _ + = < > { } [ ] | \ / : ; " ' ` ~`
- **Agresiva**: Los anteriores + acentos (`á é í ó ú à è ì ò ù ä ë ï ö ü â ê î ô û ã ẽ ĩ õ ũ ñ ç ß`)

#### Uso desde línea de comandos:
```bash
# Limpieza conservadora (mantiene acentos)
python address_enhancer.py input.csv -o output.csv --clean

# Limpieza agresiva (elimina acentos)
python address_enhancer.py input.csv -o output.csv --clean --aggressive
```

#### Uso programático:
```python
# Función independiente de limpieza
from address_enhancer import clean_address_text

clean_conservative = clean_address_text("Calle!!! Alcalá", aggressive=False)
# → "Calle Alcalá"

clean_aggressive = clean_address_text("Calle!!! Alcalá", aggressive=True)
# → "Calle Alcala"

# En completado de direcciones
result = enhancer.complete_address(
    "Calle!!! Mayor",
    clean_special_chars=True,
    aggressive=False
)

# En procesamiento en lote
enhanced = enhancer.process_address_batch(
    addresses,
    clean_special_chars=True,
    aggressive=True
)
```

### Parámetros del AddressEnhancer

```python
enhancer = AddressEnhancer(api_key="tu_api_key")  # API key opcional si no está en .env
```

### Parámetros de Procesamiento en Lote

```python
enhanced = enhancer.process_address_batch(
    addresses,
    delay=1.0,                    # Retraso entre solicitudes (segundos)
    language='es',                # Idioma de los resultados ('es', 'en', 'fr', etc.)
    clean_special_chars=False,    # 🆕 Activar limpieza de caracteres especiales
    aggressive=False              # 🆕 Usar limpieza agresiva (elimina acentos)
)
```

### Opciones de Exportación

```python
# CSV (por defecto)
enhancer.export_enhanced_addresses(addresses, 'output.csv', 'csv')

# JSON (conserva estructura compleja)
enhancer.export_enhanced_addresses(addresses, 'output.json', 'json')
```

## 🎨 Casos de Uso

### 1. Limpieza de Base de Datos de Clientes
```python
# Cargar direcciones de clientes
df_customers = pd.read_csv('customers.csv')
addresses = df_customers.to_dict('records')

# Limpiar y enriquecer
enhanced = enhancer.process_address_batch(addresses, language='es')

# Guardar resultados limpios
enhancer.export_enhanced_addresses(enhanced, 'customers_clean.csv')
```

### 2. Validación de Direcciones de Envío
```python
shipping_address = "c/ gran via 25, madrid"

# Validar completitud
analysis = enhancer.detect_incomplete_address(shipping_address)
if not analysis['is_complete']:
    print(f"Dirección incompleta. Faltan: {analysis['missing_components']}")

# Normalizar formato
normalized = enhancer.normalize_address_format(shipping_address, 'es')
print(f"Dirección normalizada: {normalized}")
```

### 3. Enriquecimiento de Datos de Ubicación
```python
location_data = {'address': 'Times Square, New York'}

# Enriquecer con información geográfica
enriched = enhancer.enrich_location_data(location_data)

print(f"Zona horaria: {enriched['timezone']['name']}")
print(f"País: {enriched['administrative_levels']['country']}")
print(f"Moneda: {enriched['geographic_info']['currency']['name']}")
```

## 🔗 Integración con Sistema Existente

El nuevo sistema es **100% compatible** con tu herramienta de geocodificación reversa existente:

- ✅ Usa las mismas dependencias
- ✅ Comparte la configuración de API key
- ✅ Mantiene el mismo formato de datos
- ✅ Extiende funcionalidades sin romper código existente

### Flujo de Trabajo Integrado

1. **Entrada**: Direcciones parciales o coordenadas
2. **Limpieza**: Normalización y corrección de errores
3. **Completado**: Uso de geocodificación directa/inversa
4. **Validación**: Verificación de componentes y códigos postales
5. **Enriquecimiento**: Adición de datos geográficos detallados
6. **Salida**: Direcciones limpias y enriquecidas

## 📚 Documentación Adicional

- **Demo interactiva**: `address_enhancement_demo.ipynb`
- **Especificaciones técnicas**: `reverse_geocoding_batch_processor/rules.md`
- **Script original**: `reverse_geocoding_batch_processor/reverse_geocoding_batch.py`

## 🤝 Contribuciones

El sistema está diseñado para ser extensible. Puedes añadir nuevas funcionalidades modificando la clase `AddressEnhancer` en `address_enhancer.py`.

## 📞 Soporte

Para problemas o preguntas sobre el sistema de enriquecimiento, consulta los ejemplos en el notebook demo o revisa la documentación técnica en el directorio del proyecto.
