# Extractor de Datos KML

Este proyecto proporciona un script de Python para extraer coordenadas e IDs de archivos KML, especialmente aquellos generados por BatchGeo.

## Características

- ✅ Extrae coordenadas (longitud, latitud, altitud) de elementos `<coordinates>`
- ✅ Extrae IDs de elementos `<Data name='id'><value>...</value></Data>`
- ✅ Extrae direcciones de elementos `<address>`
- ✅ Soporte para exportación a CSV y JSON
- ✅ Manejo robusto de errores y logging
- ✅ Interfaz de línea de comandos amigable
- ✅ Diseño modular y extensible

## Requisitos

- Python 3.6 o superior
- Librerías estándar de Python (xml.etree.ElementTree, csv, json, argparse, pathlib, logging)

## Instalación

1. Clona o descarga los archivos del proyecto
2. No se requieren dependencias adicionales (solo librerías estándar de Python)

## Uso

### Línea de Comandos

```bash
# Uso básico - mostrar resumen en consola
python kml_extractor.py archivo.kml

# Guardar en CSV
python kml_extractor.py archivo.kml --csv salida.csv

# Guardar en JSON
python kml_extractor.py archivo.kml --json salida.json

# Guardar en ambos formatos
python kml_extractor.py archivo.kml --csv salida.csv --json salida.json

# Modo verbose para depuración
python kml_extractor.py archivo.kml --verbose
```

### Uso Programático

```python
from kml_extractor import KMLExtractor

# Crear instancia del extractor
extractor = KMLExtractor("mi_archivo.kml")

# Extraer datos
data = extractor.extract_data()

# Mostrar resumen
extractor.print_summary()

# Guardar en diferentes formatos
extractor.save_to_csv("output.csv")
extractor.save_to_json("output.json")

# Acceder a los datos
for item in data:
    print(f"ID: {item['id']}")
    print(f"Coordenadas: ({item['longitude']}, {item['latitude']})")
    print(f"Dirección: {item['address']}")
```

## Estructura de Datos

Cada elemento extraído contiene los siguientes campos:

```python
{
    'placemark_index': 1,                    # Índice del placemark (1-based)
    'id': '123',                            # ID extraído de ExtendedData
    'address': '123 Main St, City, State',  # Dirección del placemark
    'longitude': -85.1255921,               # Longitud (decimal)
    'latitude': 35.0777221,                 # Latitud (decimal)
    'altitude': 0.0,                        # Altitud (decimal)
    'coordinates_raw': '-85.1255921,35.0777221,0'  # Coordenadas originales
}
```

## Ejemplo de Salida CSV

```csv
placemark_index,id,address,longitude,latitude,altitude,coordinates_raw
1,,7469 Enterprise South Boulevard Chattanooga TN 37421,-85.1255921,35.0777221,0.0,"-85.1255921,35.0777221,0"
2,1,8001 VW Drive Chattanooga TN 37416,-85.1349713,35.0763078,0.0,"-85.1349713,35.0763078,0"
3,2,7165 Engineering Drive Chattanooga TN 37421,-85.1464782,35.0813103,0.0,"-85.1464782,35.0813103,0"
```

## Pruebas

Ejecuta el script de prueba para verificar la funcionalidad:

```bash
python test_kml_extractor.py
```

## Estructura del Proyecto

```
reverse_geocoding/
├── kml_extractor.py          # Script principal
├── test_kml_extractor.py     # Script de pruebas
└── README_KML.md            # Este archivo
```

## Manejo de Errores

El script maneja varios tipos de errores:

- **Archivo no encontrado**: Verifica que la ruta del archivo KML sea correcta
- **XML malformado**: Valida la estructura del archivo KML
- **Coordenadas inválidas**: Ignora coordenadas que no se pueden parsear
- **Elementos faltantes**: Maneja graciosamente placemarks sin coordenadas o IDs

## Logging

El script utiliza el módulo `logging` de Python para proporcionar información detallada:

- **INFO**: Información general sobre el progreso
- **WARNING**: Advertencias sobre datos problemáticos
- **ERROR**: Errores que impiden el procesamiento
- **DEBUG**: Información detallada (usar con `--verbose`)

## Personalización

El script es modular y puede ser fácilmente extendido:

1. **Agregar nuevos formatos de salida**: Implementar métodos como `save_to_xml()` o `save_to_geojson()`
2. **Extraer campos adicionales**: Modificar `extract_data()` para incluir más elementos KML
3. **Filtrado de datos**: Agregar métodos para filtrar por criterios específicos
4. **Validación de coordenadas**: Implementar validación geográfica más estricta

## Licencia

Este proyecto es de código abierto y puede ser usado libremente para propósitos educativos y comerciales.

## Soporte

Para reportar problemas o sugerir mejoras, por favor contacta al equipo de desarrollo.
