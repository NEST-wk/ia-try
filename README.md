# Segmentación Inteligente de Clientes en Retail Online

## Descripción del Proyecto
Sistema de segmentación de clientes utilizando Machine Learning clásico sobre el dataset Online Retail (UCI). El proyecto incluye análisis RFM, clustering con K-Means y un dashboard interactivo orientado a usuarios no técnicos.

## Dataset
**Online Retail Dataset** - UCI Machine Learning Repository
- Datos transaccionales de retail online (2010-2011)
- 541,909 registros
- Columnas: InvoiceNo, StockCode, Description, Quantity, UnitPrice, InvoiceDate, CustomerID, Country

**Descarga del dataset:**
https://archive.ics.uci.edu/ml/datasets/Online+Retail

Coloca el archivo `Online Retail.xlsx` en la carpeta `data/`

## Estructura del Proyecto
```
ia try/
├── data/
│   └── Online Retail.xlsx          # Dataset (descargar manualmente)
├── notebooks/
│   └── analisis_segmentacion.ipynb # Análisis completo (Pasos 1-7)
├── src/
│   └── app_dashboard.py            # PMV con Streamlit (Paso 8)
├── requirements.txt
└── README.md
```

## Instalación

1. Clonar o descargar el proyecto
2. Crear entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Descargar el dataset y colocarlo en `data/Online Retail.xlsx`

## Uso

### Ejecutar Análisis Completo (Notebook)
```bash
jupyter notebook notebooks/analisis_segmentacion.ipynb
```

### Ejecutar Dashboard (PMV)
```bash
streamlit run src/app_dashboard.py
```

El dashboard se abrirá automáticamente en el navegador (http://localhost:8501)

## Metodología

### PASO 1: Comprensión del Problema
Explicación conceptual sobre clientes valiosos y la importancia de la segmentación.

### PASO 2: EDA Básico
Análisis exploratorio: estructura, valores faltantes, outliers y conclusiones.

### PASO 3: Limpieza y Agregación
Preparación y agregación de datos a nivel cliente.

### PASO 4: Modelo RFM
Cálculo de:
- **Recency**: Días desde la última compra
- **Frequency**: Número de compras
- **Monetary**: Gasto total acumulado

### PASO 5: Clustering K-Means
Segmentación no supervisada sobre RFM normalizado.

### PASO 6: Interpretación de Segmentos
Caracterización y nomenclatura de cada segmento.

### PASO 7: Árbol de Decisión Explicativo
Modelo supervisado para explicar reglas de pertenencia a segmentos.

### PASO 8: PMV - Dashboard
Producto Mínimo Viable con:
- KPIs principales
- Distribución de clientes por segmento
- Comparación de gasto
- Tabla resumen RFM

## Resultados Esperados
- Segmentos de clientes identificados y caracterizados
- Recomendaciones estratégicas por segmento
- Dashboard funcional para toma de decisiones

## Tecnologías
- Python 3.8+
- pandas, numpy
- scikit-learn
- matplotlib, seaborn, plotly
- Streamlit

## Autor
Data Science Bootcamp Project - Retail Customer Segmentation

## Licencia
MIT
