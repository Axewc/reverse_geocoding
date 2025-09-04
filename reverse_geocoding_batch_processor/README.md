# Reverse Geocoding Batch Processor

Este proyecto te permite procesar coordenadas desde archivos CSV o TXT y obtener las direcciones correspondientes usando la API de OpenCage.

## Archivos Incluidos

- `reverse_geocoding_batch.py` - Script principal con argumentos de línea de comandos
- `reverse_geocoding_simple.py` - Versión simplificada para uso fácil
- `coordenadas_ejemplo.txt` - Archivo de ejemplo con coordenadas
- `resultados_txt.csv` - Ejemplo de resultados desde TXT

## Configuración

1. Instala las dependencias:
```bash
pip install python-dotenv opencage pandas
```

2. Crea un archivo `.env` en el **directorio padre** del proyecto con tu API key de OpenCage:
```
OPENCAGE_API_KEY=tu_api_key_aqui
```

## Uso

### Opción 1: Script de Línea de Comandos (Recomendado)

```bash
# Procesar archivo CSV
python reverse_geocoding_batch.py coords.csv -o resultados.csv

# Procesar archivo TXT
python reverse_geocoding_batch.py coords.txt -o resultados.txt.csv

# Con delay personalizado (2 segundos entre requests)
python reverse_geocoding_batch.py coords.csv -o resultados.csv -d 2.0

# Especificar formato manualmente
python reverse_geocoding_batch.py coords.txt --format txt -o resultados.csv

# Limpiar caracteres especiales de las direcciones
python reverse_geocoding_batch.py coords.csv -o resultados_limpios.csv --clean

# Limpieza agresiva (remueve acentos)
python reverse_geocoding_batch.py coords.csv -o resultados_agresivos.csv --clean --aggressive

# Especificar idioma y país
python reverse_geocoding_batch.py coords.csv -o resultados.csv --language es --country-code es
```

### Opción 2: Script Simplificado

```python
from reverse_geocoding_simple import reverse_geocode_file

# Procesar archivo CSV
success = reverse_geocode_file('coords.csv', 'resultados.csv')

# Procesar archivo TXT
success = reverse_geocode_file('coords.txt', 'resultados_txt.csv')

# Procesar con limpieza y delay personalizado
success = reverse_geocode_file('coords.csv', 'resultados_limpios.csv', clean_special_chars=True, delay=2.0)
```

## Parámetros y Bandera de Línea de Comandos

Los siguientes argumentos pueden usarse al ejecutar `reverse_geocoding_batch.py`:

- `-o`, `--output`  
  **Archivo de salida**. Especifica el nombre del archivo CSV donde se guardarán los resultados.  
  *Ejemplo:* `-o resultados.csv`

- `-d`, `--delay`  
  **Delay entre requests**. Tiempo (en segundos) de espera entre cada consulta a la API para evitar límites de uso.  
  *Ejemplo:* `-d 2.0`

- `--format`  
  **Formato de entrada**. Permite forzar el tipo de archivo de entrada (`csv` o `txt`). Si no se indica, se detecta automáticamente por la extensión.  
  *Ejemplo:* `--format txt`

- `--clean`  
  **Limpieza de caracteres especiales**. Elimina símbolos problemáticos (¿?¡!@#$...) de las direcciones y campos de salida.  
  *Ejemplo:* `--clean`

- `--aggressive`  
  **Limpieza agresiva**. Además de los símbolos, elimina acentos y caracteres especiales para máxima compatibilidad.  
  *Ejemplo:* `--clean --aggressive`

- `--language`  
  **Idioma de los resultados**. Permite especificar el idioma en el que se devuelve la dirección (por defecto: `en`).  
  *Ejemplo:* `--language es`

- `--country-code`  
  **Código de país**. Bias geográfico para mejorar la precisión de los resultados en un país específico.  
  *Ejemplo:* `--country-code es`

### ¿De dónde salen estos parámetros?

Estos argumentos se definen en el script principal usando la librería `argparse` de Python.  
Al ejecutar el script, puedes combinarlos según tus necesidades para personalizar el procesamiento y el formato de los resultados.

### ¿Cómo funcionan?

- Los parámetros se pasan al script por línea de comandos.
- El script los interpreta y ajusta el comportamiento: formato de entrada, idioma, limpieza, delay, etc.
- Algunos parámetros (`language`, `country-code`, `no_annotations`) se envían directamente a la API de OpenCage para modificar la respuesta.
- Otros (`clean`, `aggressive`, `delay`) afectan el procesamiento local y la salida del archivo.

## Formatos de Archivo Soportados

### CSV
- Columnas: `lat, lng` o `latitude, longitude` (auto-detectado)
- También funciona con las primeras dos columnas si no encuentra nombres estándar
- Separador detectado automáticamente (coma, tabulación, punto y coma)

### TXT
- Formato: `latitud,longitud` o `latitud longitud`
- Líneas vacías y comentarios (que empiecen con #) son ignorados

## Archivo de Salida

El archivo CSV de salida incluye:
- `latitude` - Latitud original
- `longitude` - Longitud original  
- `address` - Dirección completa
- `country` - País
- `state` - Estado/Provincia
- `city` - Ciudad
- `postcode` - Código postal

## Consideraciones

- **Rate Limiting**: El script incluye delays entre requests para respetar los límites de la API
- **Manejo de Errores**: Coordenadas inválidas son saltadas y reportadas
- **Encoding**: Los archivos se leen y escriben en UTF-8
- **API Key**: Asegúrate de tener una API key válida de OpenCage en el directorio padre

## Ejemplos de Uso

### Procesar coordenadas de España
```bash
python reverse_geocoding_batch.py coordinates_esp_corrected.csv -o resultados_esp.csv
```

### Procesar archivo de ejemplo
```bash
python reverse_geocoding_batch.py coordenadas_ejemplo.txt -o resultados_ejemplo.csv
```

### Procesar y limpiar direcciones
```bash
python reverse_geocoding_batch.py coordinates_esp_corrected.csv -o resultados_limpios.csv --clean
```

### Procesar con limpieza agresiva
```bash
python reverse_geocoding_batch.py coordinates_esp_corrected.csv -o resultados_agresivos.csv --clean --aggressive
```

### Procesar con idioma y país específico
```bash
python reverse_geocoding_batch.py coordinates_esp_corrected.csv -o resultados.csv --language es --country-code es
```

### Ver resultados
```python
import pandas as pd
df = pd.read_csv('resultados_esp.csv')
print(df.head())
```
