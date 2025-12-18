# Guía de Uso - Segmentación de Clientes

## 📋 Contenido del Proyecto

```
ia try/
├── data/                           # Carpeta de datos
│   └── Online Retail.xlsx         # Dataset (descargarlo manualmente)
├── notebooks/                      # Análisis y desarrollo
│   └── analisis_segmentacion.ipynb  # Notebook completo (Pasos 1-7)
├── src/                           # Código fuente del PMV
│   └── app_dashboard.py          # Dashboard Streamlit (Paso 8)
├── requirements.txt              # Dependencias del proyecto
├── README.md                     # Documentación principal
└── GUIA_USO.md                  # Esta guía
```

## 🚀 Inicio Rápido

### 1. Descargar el Dataset

El dataset **Online Retail** está disponible en el repositorio de UCI Machine Learning:

**URL**: https://archive.ics.uci.edu/ml/datasets/Online+Retail

**Pasos:**
1. Visita el enlace anterior
2. Descarga el archivo `Online Retail.xlsx`
3. Colócalo en la carpeta `data/` del proyecto

### 2. Instalar Dependencias

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# Instalar paquetes
pip install -r requirements.txt
```

### 3. Ejecutar el Análisis Completo (Notebook)

```bash
# Iniciar Jupyter Notebook
jupyter notebook

# Abrir: notebooks/analisis_segmentacion.ipynb
# Ejecutar todas las celdas en orden (Cell > Run All)
```

**El notebook incluye:**
- ✅ PASO 1: Comprensión del problema (explicación conceptual)
- ✅ PASO 2: EDA básico
- ✅ PASO 3: Limpieza y agregación
- ✅ PASO 4: Cálculo RFM
- ✅ PASO 5: Clustering K-Means
- ✅ PASO 6: Interpretación de segmentos
- ✅ PASO 7: Árbol de decisión explicativo
- ✅ PASO 8: Guardado de datos para PMV

### 4. Ejecutar el Dashboard (PMV)

```bash
# Desde la raíz del proyecto
streamlit run src/app_dashboard.py
```

El dashboard se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📊 Usando el Dashboard

### Opción A: Cargar Datos Pre-procesados

Si ya ejecutaste el notebook:

1. En la barra lateral, marca "Usar datos pre-procesados"
2. El dashboard cargará automáticamente los resultados guardados

### Opción B: Procesar Datos Desde Cero

Si quieres procesar nuevos datos:

1. **NO marques** "Usar datos pre-procesados"
2. Haz clic en "Browse files" en la barra lateral
3. Selecciona el archivo `Online Retail.xlsx`
4. El sistema procesará automáticamente:
   - Limpieza de datos
   - Cálculo de RFM
   - Clustering
   - Asignación de segmentos
5. Ajusta el número de segmentos con el slider (opcional)

## 📈 Interpretando los Resultados

### KPIs Principales

- **Total de Clientes**: Número de clientes únicos analizados
- **Número de Segmentos**: Grupos identificados por clustering
- **Ingreso Total**: Suma de todo el gasto de clientes
- **Ingreso Promedio por Segmento**: Gasto promedio de cada grupo

### Segmentos Típicos Identificados

**1. Champions** 🏆
- Clientes más valiosos
- Alta frecuencia y gasto reciente
- Prioridad: CRÍTICA

**2. Loyal Customers** ⭐
- Base sólida del negocio
- Compran regularmente
- Prioridad: ALTA

**3. Occasional Buyers** 📊
- Compran esporádicamente
- Potencial de crecimiento
- Prioridad: MEDIA

**4. At Risk** ⚠️
- Clientes inactivos
- Riesgo de abandono
- Prioridad: URGENTE

### Visualizaciones Disponibles

1. **Distribución de Clientes**: Número y proporción de clientes por segmento
2. **Comparación de Gasto**: Ingresos totales y promedio por segmento
3. **Clusters en Espacio RFM**: Visualización 2D de la segmentación
4. **Tabla Resumen**: Métricas consolidadas por segmento
5. **Insights**: Recomendaciones estratégicas específicas

## 🎯 Aplicando los Resultados

### Para el Equipo de Marketing

1. **Personalizar Campañas**: Usa los segmentos para crear mensajes diferenciados
2. **Priorizar Inversión**: Concentra recursos en segmentos de alto valor
3. **Medir ROI**: Compara resultados entre segmentos

### Para el Equipo Comercial

1. **Identificar Oportunidades**: Champions y Loyal para upselling
2. **Prevenir Abandono**: Actuar rápidamente con "At Risk"
3. **Desarrollar Clientes**: Mover "Occasional" a categorías superiores

### Para la Dirección

1. **Entender la Base de Clientes**: Composición y valor de cada grupo
2. **Proyectar Ingresos**: Usar patrones de gasto por segmento
3. **Tomar Decisiones**: Estrategias basadas en datos reales

## 🔧 Personalización

### Cambiar Número de Segmentos

En el notebook (celda de clustering):
```python
optimal_k = 5  # Cambiar de 4 a 5 segmentos
```

En el dashboard:
- Usar el slider "Número de segmentos" en la barra lateral

### Ajustar Nombres de Segmentos

En el notebook o dashboard, modificar la función `assign_segment_name()`:
```python
def assign_segment_name(cluster_id, cluster_avg):
    # Personalizar lógica aquí
    if condicion:
        return 'Nombre Personalizado'
```

### Modificar Visualizaciones

En `app_dashboard.py`, las visualizaciones usan Plotly:
```python
# Ejemplo: cambiar colores
color_discrete_sequence=px.colors.qualitative.Pastel
```

## ❓ Solución de Problemas

### Error: "No module named 'streamlit'"
```bash
pip install streamlit
```

### Error: "Archivos pre-procesados no encontrados"
- Ejecuta primero el notebook completo
- O usa la opción de cargar archivo en el dashboard

### Error: "FileNotFoundError: Online Retail.xlsx"
- Asegúrate de que el archivo está en `data/`
- Verifica el nombre exacto del archivo

### Dashboard no se abre automáticamente
- Abre manualmente: http://localhost:8501
- Si el puerto está ocupado, Streamlit usará otro (verlo en terminal)

### Gráficos no se visualizan
```bash
pip install plotly --upgrade
```

## 📝 Notas Importantes

- **Dataset**: El archivo debe ser Excel (.xlsx), no CSV
- **Tiempo de Procesamiento**: Depende del tamaño de los datos (~30 segundos para 500k registros)
- **Memoria**: Recomendado mínimo 4GB RAM
- **Python**: Versión 3.8 o superior

## 🔄 Actualizando la Segmentación

Para mantener la segmentación actualizada:

1. **Mensualmente**: Re-ejecutar el notebook con datos nuevos
2. **Guardar Resultados**: Los archivos `.pkl` y `.csv` en `data/`
3. **Comparar**: Monitorear cambios en la distribución de segmentos
4. **Ajustar Estrategias**: Según evolución de cada segmento

## 📚 Recursos Adicionales

### Entendiendo RFM

- **Recency**: Clientes recientes son más propensos a comprar
- **Frequency**: Clientes frecuentes son más leales
- **Monetary**: Clientes de alto gasto tienen mayor valor

### Sobre K-Means

- Algoritmo no supervisado que agrupa datos similares
- Número de clusters debe balancear separación e interpretabilidad
- StandardScaler normaliza para que todas las variables tengan igual peso

### Métricas de Evaluación

- **Inercia**: Suma de distancias dentro de clusters (menor = mejor)
- **Silhouette**: Calidad de separación entre clusters (mayor = mejor)
- **Interpretabilidad**: Más importante que métricas perfectas

## 🤝 Soporte

Para preguntas o problemas:
1. Revisa esta guía completa
2. Consulta el README.md principal
3. Verifica los comentarios en el código del notebook

---

**¡Éxito con tu análisis de segmentación de clientes!** 🎉
