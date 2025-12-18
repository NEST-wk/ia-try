# INSTRUCCIONES PARA DESCARGAR EL DATASET

Este proyecto requiere el dataset "Online Retail" de UCI Machine Learning Repository.

## Opción 1: Descarga Directa desde UCI

1. Visita: https://archive.ics.uci.edu/ml/datasets/Online+Retail
2. Haz clic en "Data Folder"
3. Descarga el archivo: `Online Retail.xlsx`
4. Colócalo en la carpeta `data/` de este proyecto

## Opción 2: Descarga mediante Script Python

Si prefieres automatizar la descarga, ejecuta el siguiente script:

```python
import requests
import os

# URL del dataset
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"

# Crear carpeta data si no existe
os.makedirs('data', exist_ok=True)

# Descargar archivo
print("Descargando dataset...")
response = requests.get(url)

# Guardar archivo
with open('data/Online Retail.xlsx', 'wb') as f:
    f.write(response.content)

print("✓ Dataset descargado exitosamente en: data/Online Retail.xlsx")
```

Guarda este código como `download_dataset.py` y ejecútalo:
```bash
python download_dataset.py
```

## Verificar la Descarga

Después de descargar, verifica:

```bash
# Windows PowerShell
Get-ChildItem data

# Deberías ver:
# Online Retail.xlsx
```

## Información del Dataset

- **Nombre**: Online Retail Dataset
- **Fuente**: UCI Machine Learning Repository
- **Tamaño**: ~23 MB
- **Registros**: 541,909 transacciones
- **Periodo**: 01/12/2010 - 09/12/2011
- **Columnas**: 8 (InvoiceNo, StockCode, Description, Quantity, UnitPrice, InvoiceDate, CustomerID, Country)

## Problemas Comunes

### No puedo acceder a UCI
- El sitio puede estar temporalmente caído
- Prueba más tarde o usa un mirror alternativo

### Archivo corrupto
- Verifica que el archivo tiene ~23 MB
- Re-descarga si es necesario

### Formato incorrecto
- Asegúrate de descargar el archivo .xlsx, NO el .csv
- El nombre exacto debe ser: `Online Retail.xlsx`

---

Una vez descargado, podrás ejecutar el notebook y el dashboard sin problemas.
