"""
Dashboard de Segmentación de Clientes - Producto Mínimo Viable (PMV)
=====================================================================

Dashboard interactivo para usuarios no técnicos que permite:
- Cargar datos de retail online
- Ejecutar segmentación RFM automática
- Visualizar resultados y KPIs
- Tomar decisiones de negocio basadas en datos

Autor: Data Science Bootcamp
Fecha: Diciembre 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import silhouette_score, confusion_matrix, classification_report, accuracy_score
import pickle
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Importar Groq AI (API más libre y rápida)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Configuración de la página
st.set_page_config(
    page_title="Segmentación de Clientes | Retail Online",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    /* Efecto Glass para Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.1) 0%, 
            rgba(118, 75, 162, 0.1) 100%) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Mejorar contenido del sidebar */
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    /* Títulos del sidebar con efecto glass */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #667eea !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Inputs del sidebar con glass effect */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Botones del sidebar con glass effect */
    [data-testid="stSidebar"] button {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.8) 0%, 
            rgba(118, 75, 162, 0.8) 100%) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 1) 0%, 
            rgba(118, 75, 162, 1) 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Separadores del sidebar */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .segment-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

@st.cache_data
def load_data(file):
    """Cargar datos desde archivo Excel"""
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None


def clean_data(df):
    """Limpiar y preparar datos"""
    with st.spinner("Limpiando datos..."):
        # Crear copia
        df_clean = df.copy()
        
        initial_records = len(df_clean)
        
        # Eliminar CustomerID nulos
        df_clean = df_clean[df_clean['CustomerID'].notna()]
        
        # Eliminar cancelaciones
        df_clean = df_clean[~df_clean['InvoiceNo'].astype(str).str.startswith('C')]
        
        # Eliminar valores negativos o cero
        df_clean = df_clean[df_clean['Quantity'] > 0]
        df_clean = df_clean[df_clean['UnitPrice'] > 0]
        
        # Convertir fecha
        df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])
        
        # Calcular valor total
        df_clean['TotalAmount'] = df_clean['Quantity'] * df_clean['UnitPrice']
        
        final_records = len(df_clean)
        removed_pct = ((initial_records - final_records) / initial_records) * 100
        
        st.success(f"✓ Limpieza completada: {final_records:,} transacciones válidas ({removed_pct:.1f}% eliminadas)")
        
        return df_clean


def calculate_rfm(df_clean):
    """Calcular métricas RFM"""
    with st.spinner("Calculando métricas RFM..."):
        # Fecha de referencia
        reference_date = df_clean['InvoiceDate'].max() + timedelta(days=1)
        
        # Agregar a nivel cliente
        customer_data = df_clean.groupby('CustomerID').agg({
            'InvoiceNo': 'nunique',
            'TotalAmount': 'sum',
            'InvoiceDate': 'max'
        }).reset_index()
        
        customer_data.columns = ['CustomerID', 'NumPurchases', 'TotalSpent', 'LastPurchaseDate']
        
        # Calcular RFM
        customer_data['Recency'] = (reference_date - customer_data['LastPurchaseDate']).dt.days
        customer_data['Frequency'] = customer_data['NumPurchases']
        customer_data['Monetary'] = customer_data['TotalSpent']
        
        rfm = customer_data[['CustomerID', 'Recency', 'Frequency', 'Monetary']].copy()
        
        st.success(f"✓ RFM calculado para {len(rfm):,} clientes")
        
        return rfm


def perform_clustering(rfm, n_clusters=4):
    """Aplicar K-Means clustering"""
    with st.spinner("Ejecutando clustering K-Means..."):
        # Normalizar
        scaler = StandardScaler()
        rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])
        
        # K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)
        
        st.success(f"✓ Clustering completado: {n_clusters} segmentos identificados")
        
        return rfm, kmeans, scaler


def assign_segment_names(rfm):
    """Asignar nombres descriptivos a los segmentos"""
    cluster_avg = rfm.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean()
    
    segment_names = {}
    for cluster_id in rfm['Cluster'].unique():
        recency = cluster_avg.loc[cluster_id, 'Recency']
        frequency = cluster_avg.loc[cluster_id, 'Frequency']
        monetary = cluster_avg.loc[cluster_id, 'Monetary']
        
        if recency < 50 and frequency > 5 and monetary > 2000:
            name = 'Champions'
        elif recency < 100 and frequency > 3 and monetary > 1000:
            name = 'Loyal Customers'
        elif recency > 200 and frequency < 3:
            name = 'At Risk'
        else:
            name = 'Occasional Buyers'
        
        segment_names[cluster_id] = name
    
    rfm['Segment'] = rfm['Cluster'].map(segment_names)
    
    return rfm, segment_names


def train_decision_tree(rfm, max_depth=4, min_samples_split=100, min_samples_leaf=50):
    """Entrenar árbol de decisión explicativo"""
    X = rfm[['Recency', 'Frequency', 'Monetary']]
    y = rfm['Cluster']
    
    tree_model = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        random_state=42
    )
    
    tree_model.fit(X, y)
    
    # Calcular predicciones y métricas
    y_pred = tree_model.predict(X)
    
    return tree_model, X, y, y_pred


def evaluate_clustering(rfm_scaled, max_k=10):
    """Evaluar diferentes valores de K para clustering"""
    K_range = range(2, max_k + 1)
    inertias = []
    silhouette_scores_list = []
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(rfm_scaled)
        inertias.append(kmeans.inertia_)
        silhouette_scores_list.append(silhouette_score(rfm_scaled, labels))
    
    return K_range, inertias, silhouette_scores_list


def list_available_groq_models():
    """Listar modelos disponibles en Groq"""
    # Modelos disponibles en Groq (todos gratis)
    return [
        'llama-3.3-70b-versatile',  # Recomendado - balance velocidad/calidad
        'llama-3.1-70b-versatile',
        'mixtral-8x7b-32768',
        'gemma2-9b-it',
        'llama3-70b-8192',
        'llama3-8b-8192'
    ]


def initialize_groq(api_key, show_debug=False):
    """Inicializar Groq API"""
    try:
        client = Groq(api_key=api_key)
        
        # Intentar modelos disponibles
        available_models = list_available_groq_models()
        
        if show_debug:
            st.write(f"🔍 Modelos disponibles: {len(available_models)}")
        
        # Intentar conectar con el primer modelo
        for model_name in available_models:
            try:
                if show_debug:
                    st.write(f"Probando: {model_name}...")
                
                # Probar con un mensaje simple
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=10
                )
                
                st.success(f"✅ Conectado con: {model_name}")
                return client, model_name
                
            except Exception as model_error:
                if show_debug:
                    st.write(f"❌ {model_name}: {str(model_error)[:80]}")
                continue
        
        st.error("No se pudo conectar con ningún modelo de Groq")
        return None, None
        
    except Exception as e:
        st.error(f"Error de configuración: {e}")
        return None, None


def get_chatbot_context(rfm):
    """Generar contexto completo sobre TODOS los análisis para el chatbot"""
    
    # ===== RESUMEN GENERAL =====
    context = f"""Eres streetviewer, un asistente experto en análisis de segmentación de clientes para retail online.
Tienes acceso a TODO el análisis completo del dashboard con 6 pestañas.

═══════════════════════════════════════════════════════════
📊 RESUMEN GENERAL DEL ANÁLISIS
═══════════════════════════════════════════════════════════
- Total de clientes: {len(rfm):,}
- Número de segmentos: {rfm['Cluster'].nunique()}
- Segmentos identificados: {', '.join(sorted(rfm['Segment'].unique()))}
- Algoritmo de clustering: K-Means con K={rfm['Cluster'].nunique()}
- Método de segmentación: Análisis RFM + Machine Learning

═══════════════════════════════════════════════════════════
📈 ANÁLISIS EXPLORATORIO DE DATOS (EDA)
═══════════════════════════════════════════════════════════

DISTRIBUCIONES PRINCIPALES:
- Recency: Rango {rfm['Recency'].min():.0f} - {rfm['Recency'].max():.0f} días
  · Mediana: {rfm['Recency'].median():.0f} días
  · Desv. estándar: {rfm['Recency'].std():.0f} días
  
- Frequency: Rango {rfm['Frequency'].min():.0f} - {rfm['Frequency'].max():.0f} compras
  · Mediana: {rfm['Frequency'].median():.1f} compras
  · Desv. estándar: {rfm['Frequency'].std():.1f} compras
  · Clientes con 1 sola compra: {(rfm['Frequency'] == 1).sum()} ({(rfm['Frequency'] == 1).sum()/len(rfm)*100:.1f}%)
  
- Monetary: Rango £{rfm['Monetary'].min():,.2f} - £{rfm['Monetary'].max():,.2f}
  · Mediana: £{rfm['Monetary'].median():,.2f}
  · Desv. estándar: £{rfm['Monetary'].std():,.2f}
  · Ingreso total: £{rfm['Monetary'].sum():,.2f}

CORRELACIONES RFM:
- Frequency vs Monetary: Alta correlación positiva (clientes frecuentes gastan más)
- Recency vs Frequency: Correlación negativa moderada (clientes activos compran más)
- Recency vs Monetary: Correlación negativa (clientes recientes gastan más)

═══════════════════════════════════════════════════════════
🎯 ANÁLISIS RFM DETALLADO
═══════════════════════════════════════════════════════════

MÉTRICAS GLOBALES:
- Recency promedio: {rfm['Recency'].mean():.0f} días (último contacto)
- Frequency promedio: {rfm['Frequency'].mean():.1f} compras por cliente
- Monetary promedio: £{rfm['Monetary'].mean():,.2f} por cliente
- Ticket promedio: £{rfm['Monetary'].sum()/rfm['Frequency'].sum():,.2f} por compra

SEGMENTACIÓN RFM:
El análisis divide a los clientes en cuartiles (Q1-Q4) para cada métrica:
- R_Score: 4 = compradores muy recientes, 1 = inactivos
- F_Score: 4 = muy frecuentes, 1 = ocasionales  
- M_Score: 4 = alto valor, 1 = bajo valor
- RFM_Score: Concatenación de los tres scores

═══════════════════════════════════════════════════════════
🔍 CLUSTERING K-MEANS (K={rfm['Cluster'].nunique()})
═══════════════════════════════════════════════════════════

CARACTERÍSTICAS DE LOS CLUSTERS:"""
    
    # Análisis detallado por cluster
    for cluster_id in sorted(rfm['Cluster'].unique()):
        cluster_data = rfm[rfm['Cluster'] == cluster_id]
        segment_name = cluster_data['Segment'].iloc[0]
        
        context += f"""

Cluster {cluster_id} - {segment_name}:
- Tamaño: {len(cluster_data):,} clientes ({len(cluster_data)/len(rfm)*100:.1f}%)
- Centroide RFM:
  · Recency: {cluster_data['Recency'].mean():.0f} días
  · Frequency: {cluster_data['Frequency'].mean():.1f} compras
  · Monetary: £{cluster_data['Monetary'].mean():,.2f}
- Valor total: £{cluster_data['Monetary'].sum():,.2f} ({cluster_data['Monetary'].sum()/rfm['Monetary'].sum()*100:.1f}% del total)
- Valor por cliente: £{cluster_data['Monetary'].mean():,.2f}"""
    
    # Interpretación de segmentos
    context += """

═══════════════════════════════════════════════════════════
👥 INTERPRETACIÓN DE SEGMENTOS
═══════════════════════════════════════════════════════════
"""
    
    # Análisis detallado de cada segmento
    segment_strategies = {
        'Champions': {
            'perfil': 'Mejores clientes - Compran frecuente y recientemente, gastan mucho',
            'comportamiento': 'Altamente comprometidos, alta lealtad, embajadores de marca',
            'estrategia': 'Recompensas VIP, programa de fidelización premium, early access a productos',
            'riesgo': 'Bajo - Mantener satisfacción',
            'prioridad': 'MÁXIMA'
        },
        'Loyal Customers': {
            'perfil': 'Clientes leales - Compran con regularidad, buen valor',
            'comportamiento': 'Consistentes, responden bien a comunicaciones',
            'estrategia': 'Upselling/cross-selling, programas de puntos, contenido exclusivo',
            'riesgo': 'Bajo-Medio - Proteger de competencia',
            'prioridad': 'ALTA'
        },
        'Potential Loyalist': {
            'perfil': 'Potencial leal - Clientes recientes con buena frecuencia',
            'comportamiento': 'En fase de adopción, responden a incentivos',
            'estrategia': 'Nutrición de relación, ofertas personalizadas, onboarding mejorado',
            'riesgo': 'Medio - Vulnerable a competencia',
            'prioridad': 'ALTA'
        },
        'Recent Customers': {
            'perfil': 'Nuevos compradores - Primera/segunda compra reciente',
            'comportamiento': 'Explorando la marca, formando opiniones',
            'estrategia': 'Welcome series, educación de producto, incentivos para segunda compra',
            'riesgo': 'Alto - No establecido vínculo',
            'prioridad': 'MEDIA-ALTA'
        },
        'Promising': {
            'perfil': 'Prometedores - Compradores recientes con potencial',
            'comportamiento': 'Interesados pero necesitan activación',
            'estrategia': 'Ofertas especiales, recomendaciones personalizadas, engagement campaigns',
            'riesgo': 'Medio-Alto - Necesitan activación',
            'prioridad': 'MEDIA'
        },
        'Need Attention': {
            'perfil': 'Requieren atención - Antes activos, ahora decayendo',
            'comportamiento': 'Disminuyendo frecuencia, en riesgo de pérdida',
            'estrategia': 'Campañas de reactivación, encuestas de feedback, ofertas win-back',
            'riesgo': 'Alto - Pérdida inminente',
            'prioridad': 'ALTA'
        },
        'About to Sleep': {
            'perfil': 'A punto de dormir - Inactividad prolongada',
            'comportamiento': 'Alejándose de la marca, posible insatisfacción',
            'estrategia': 'Campañas agresivas de reengagement, descuentos significativos',
            'riesgo': 'Muy Alto - Casi perdidos',
            'prioridad': 'MEDIA'
        },
        'At Risk': {
            'perfil': 'En riesgo - Buenos clientes que no compran hace tiempo',
            'comportamiento': 'Desconectados, alto valor histórico en juego',
            'estrategia': 'Contacto directo, ofertas personalizadas VIP, recuperación urgente',
            'riesgo': 'CRÍTICO - Alto valor en riesgo',
            'prioridad': 'MÁXIMA'
        },
        'Cannot Lose Them': {
            'perfil': 'No podemos perderlos - Clientes de alto valor inactivos',
            'comportamiento': 'Antes top customers, ahora inactivos - ALERTA ROJA',
            'estrategia': 'Intervención directa CEO/gerencia, ofertas ultra-premium, recuperación a cualquier costo',
            'riesgo': 'CRÍTICO - Pérdida de alto impacto',
            'prioridad': 'EMERGENCIA'
        },
        'Hibernating': {
            'perfil': 'Hibernando - Largo tiempo sin actividad',
            'comportamiento': 'Muy probablemente perdidos, bajo engagement',
            'estrategia': 'Win-back campaigns de bajo costo, ofertas masivas, último intento',
            'riesgo': 'Muy Alto - Probablemente perdidos',
            'prioridad': 'BAJA'
        },
        'Lost': {
            'perfil': 'Perdidos - Sin actividad reciente, bajo valor histórico',
            'comportamiento': 'Churn completo, muy baja probabilidad de retorno',
            'estrategia': 'Campañas masivas de bajo costo, focus en adquisición nueva',
            'riesgo': 'Máximo - Churn completo',
            'prioridad': 'MUY BAJA'
        }
    }
    
    for segment in sorted(rfm['Segment'].unique()):
        segment_data = rfm[rfm['Segment'] == segment]
        info = segment_strategies.get(segment, {})
        
        context += f"""

🏷️ {segment.upper()}
{'-' * 60}
- Tamaño: {len(segment_data):,} clientes ({len(segment_data)/len(rfm)*100:.1f}%)
- Perfil: {info.get('perfil', 'N/A')}
- Comportamiento: {info.get('comportamiento', 'N/A')}
- Estrategia recomendada: {info.get('estrategia', 'N/A')}
- Nivel de riesgo: {info.get('riesgo', 'N/A')}
- Prioridad: {info.get('prioridad', 'N/A')}

Métricas clave:
- Recency media: {segment_data['Recency'].mean():.0f} días
- Frequency media: {segment_data['Frequency'].mean():.1f} compras
- Monetary medio: £{segment_data['Monetary'].mean():,.2f}
- Valor total: £{segment_data['Monetary'].sum():,.2f}
- ROI potencial: {'ALTO' if segment in ['Champions', 'Loyal Customers', 'Cannot Lose Them', 'At Risk'] else 'MEDIO' if segment in ['Potential Loyalist', 'Need Attention'] else 'BAJO'}"""
    
    context += """

═══════════════════════════════════════════════════════════
🌳 ÁRBOL DE DECISIÓN - REGLAS DE CLASIFICACIÓN
═══════════════════════════════════════════════════════════

El modelo de árbol de decisión genera reglas interpretables para clasificar clientes:
- Entradas: Recency, Frequency, Monetary (escaladas)
- Salida: Predicción de segmento
- Parámetros optimizables: max_depth, min_samples_split, min_samples_leaf

INTERPRETACIÓN DE REGLAS:
Las reglas del árbol muestran los umbrales exactos de RFM que definen cada segmento.
Ejemplo: "Si Recency <= 50 días Y Frequency > 5 compras → Champions"

MÉTRICAS DEL MODELO:
- Accuracy: Mide precisión general de clasificación
- Confusion Matrix: Muestra aciertos/errores por segmento
- Feature Importance: Recency suele ser la más influyente

═══════════════════════════════════════════════════════════
💡 INSIGHTS ACCIONABLES
═══════════════════════════════════════════════════════════

1. PRIORIZACIÓN DE RECURSOS:
   - MÁXIMA: Champions, At Risk, Cannot Lose Them
   - ALTA: Loyal Customers, Potential Loyalist, Need Attention
   - MEDIA: Recent Customers, Promising, About to Sleep
   - BAJA: Hibernating, Lost

2. OPTIMIZACIÓN DE PRESUPUESTO:
   - 60% en retención de alto valor (Champions, Loyal, At Risk)
   - 25% en desarrollo (Potential Loyalist, Recent)
   - 15% en recuperación (Need Attention, Cannot Lose)

3. MÉTRICAS A MONITOREAR:
   - Tasa de migración entre segmentos
   - CLV (Customer Lifetime Value) por segmento
   - Churn rate en segmentos de riesgo
   - Efectividad de campañas por segmento

═══════════════════════════════════════════════════════════
🎯 TU MISIÓN COMO STREETVIEWER
═══════════════════════════════════════════════════════════

Debes ayudar a los usuarios a:
1. ✅ Entender CUALQUIER aspecto del análisis completo (6 pestañas)
2. ✅ Interpretar métricas RFM, clusters, y reglas del árbol
3. ✅ Tomar decisiones estratégicas basadas en datos
4. ✅ Diseñar campañas específicas por segmento
5. ✅ Optimizar presupuestos de marketing
6. ✅ Identificar oportunidades y riesgos
7. ✅ Explicar el análisis a stakeholders no técnicos

ESTILO DE RESPUESTA:
- 🎯 Claro y conciso, orientado a negocios
- 📊 Fundamentado en los datos proporcionados arriba
- 💼 Lenguaje profesional pero accesible
- 🇪🇸 Siempre en español
- 💡 Proactivo: sugiere insights adicionales relevantes
- 🔢 Usa números específicos del análisis cuando sea posible

¡Ahora tienes CONTEXTO COMPLETO del dashboard entero! 🚀"""
    
    return context


# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

def main():
    """Función principal del dashboard"""
    
    # Título
    st.markdown('<p class="main-title">📊 Segmentación Inteligente de Clientes</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Dashboard de Análisis RFM y Clustering para Retail Online</p>', unsafe_allow_html=True)
    
    # Inicializar session state para el chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'groq_client' not in st.session_state:
        st.session_state.groq_client = None
    if 'groq_model' not in st.session_state:
        st.session_state.groq_model = None
    
    # Barra lateral
    st.sidebar.title("⚙️ Configuración")
    st.sidebar.markdown("---")
    
    # Opción 1: Cargar datos pre-procesados
    use_preprocessed = st.sidebar.checkbox("Usar datos pre-procesados", value=False)
    
    if use_preprocessed:
        try:
            rfm = pd.read_csv('data/rfm_segments.csv')
            with open('data/segment_names.pkl', 'rb') as f:
                segment_names = pickle.load(f)
            
            st.sidebar.success("✓ Datos pre-procesados cargados")
            
        except FileNotFoundError:
            st.sidebar.error("❌ Archivos pre-procesados no encontrados. Ejecuta el notebook primero.")
            return
    
    else:
        # Opción 2: Cargar y procesar datos desde archivo
        st.sidebar.subheader("📁 Cargar Datos")
        uploaded_file = st.sidebar.file_uploader(
            "Selecciona el archivo Online Retail.xlsx",
            type=['xlsx', 'xls']
        )
        
        if uploaded_file is None:
            st.info("👈 Por favor, carga el archivo de datos desde la barra lateral para comenzar.")
            
            # Información adicional
            st.markdown("---")
            st.subheader("📖 Acerca de este Dashboard")
            st.markdown("""
            Este dashboard te permite:
            - **Cargar datos** transaccionales de retail online
            - **Calcular automáticamente** métricas RFM (Recency, Frequency, Monetary)
            - **Segmentar clientes** usando K-Means clustering
            - **Visualizar resultados** con gráficos interactivos
            - **Tomar decisiones** estratégicas basadas en datos
            
            **Instrucciones:**
            1. Descarga el dataset 'Online Retail' desde UCI ML Repository
            2. Carga el archivo usando el selector de la barra lateral
            3. El sistema procesará automáticamente los datos
            4. Explora los KPIs y visualizaciones generadas
            """)
            
            return
        
        # Procesar datos
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔧 Procesamiento")
        
        # Cargar
        df = load_data(uploaded_file)
        if df is None:
            return
        
        st.sidebar.info(f"Registros cargados: {len(df):,}")
        
        # Limpiar
        df_clean = clean_data(df)
        
        # Calcular RFM
        rfm = calculate_rfm(df_clean)
        
        # Clustering
        n_clusters = st.sidebar.slider("Número de segmentos", 2, 8, 4)
        rfm, kmeans_model, scaler = perform_clustering(rfm, n_clusters)
        
        # Asignar nombres
        rfm, segment_names = assign_segment_names(rfm)
    
    # ========================================================================
    # CHATBOT EN SIDEBAR
    # ========================================================================
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 streetviewer")
    
    # Inicializar estado del chat flotante
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = False
    
    if GROQ_AVAILABLE:
        # Configuración de API Key
        with st.sidebar.expander("⚙️ Configurar API Key de Groq", expanded=False):
            st.markdown("""
            Para usar el chatbot necesitas una API key **GRATUITA** de Groq.
            
            **Obtener API Key (GRATIS):**
            1. Ve a [Groq Console](https://console.groq.com/keys)
            2. Crea una cuenta gratuita
            3. Genera tu API key
            4. Pégala aquí abajo
            
            **Ventajas de Groq:**
            - ✅ 100% gratuito
            - ✅ 14,000+ tokens/minuto
            - ✅ Ultra rápido
            - ✅ Modelos open source (Llama, Mixtral, Gemma)
            """)
            
            # Intentar cargar desde secrets primero
            api_key = None
            try:
                if 'GROQ_API_KEY' in st.secrets:
                    api_key = st.secrets['GROQ_API_KEY']
                    st.success("✓ API Key cargada desde secrets")
            except:
                pass
            
            # Si no hay en secrets, permitir input manual
            if api_key is None:
                api_key = st.text_input(
                    "Groq API Key",
                    type="password",
                    placeholder="gsk_...",
                    help="Tu API key no se guarda, solo se usa durante la sesión"
                )
        
        # Botón para ver modelos disponibles
        if api_key and st.button("🔍 Ver Modelos Disponibles", use_container_width=True):
            models = list_available_groq_models()
            st.success(f"✅ {len(models)} modelos disponibles:")
            for model in models:
                st.write(f"  • {model}")
        
        # Inicializar modelo si hay API key
        if api_key:
            if 'groq_client' not in st.session_state or st.session_state.groq_client is None:
                with st.sidebar.status("🔄 Inicializando chatbot...", expanded=True) as status:
                    client, model_name = initialize_groq(api_key, show_debug=True)
                    if client:
                        st.session_state.groq_client = client
                        st.session_state.groq_model = model_name
                        status.update(label="✓ Chatbot listo", state="complete", expanded=False)
                    else:
                        status.update(label="❌ Error al inicializar", state="error", expanded=True)
            
            # Botón para abrir chat flotante
            if st.session_state.groq_client:
                if st.sidebar.button("💬 Abrir Chat Flotante", use_container_width=True, type="primary"):
                    st.session_state.chat_open = True
                    st.rerun()
        
        elif api_key:
            st.sidebar.warning("⚠️ El chatbot no pudo inicializarse. Revisa los mensajes arriba.")
        else:
            st.sidebar.info("⬆️ Configura tu API key para activar el chatbot")
    
    else:
        st.sidebar.warning("⚠️ Instala groq para usar el chatbot")
        st.sidebar.code("pip install groq", language="bash")
    
    # ========================================================================
    # CHAT FLOTANTE - DISEÑO MEJORADO Y RESPONSIVE
    # ========================================================================
    
    # CSS mejorado para el chat flotante
    if st.session_state.chat_open and GROQ_AVAILABLE and 'groq_client' in st.session_state and st.session_state.groq_client:
        st.markdown("""
        <style>
        /* Chat flotante - Posicionamiento responsive */
        .chat-float-wrapper {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            width: 400px;
            max-width: calc(100vw - 40px);
        }
        
        /* Popover del chat */
        [data-testid="stPopover"] {
            position: fixed !important;
            bottom: 90px !important;
            right: 20px !important;
            z-index: 9999 !important;
            width: 420px !important;
            max-width: calc(100vw - 40px) !important;
        }
        
        /* Botón flotante circular mejorado */
        .chat-fab-button {
            position: fixed !important;
            bottom: 20px !important;
            right: 20px !important;
            z-index: 9998 !important;
            width: 60px !important;
            height: 60px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.5) !important;
            border: none !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        .chat-fab-button:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6) !important;
        }
        
        /* Contenedor del popover mejorado */
        div[data-testid="stPopover"] > div {
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            overflow: hidden;
            padding: 0 !important;
        }
        
        /* Header del chat */
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px;
            border-radius: 16px 16px 0 0;
        }
        
        /* Botones responsive */
        .chat-buttons {
            display: flex;
            gap: 8px;
            width: 100%;
            margin-top: 12px;
        }
        
        .chat-btn-primary {
            flex: 3;
            min-width: 0;
        }
        
        .chat-btn-secondary {
            flex: 1;
            min-width: 0;
        }
        
        /* Arreglar botones en móvil */
        @media (max-width: 768px) {
            [data-testid="stPopover"] {
                width: calc(100vw - 20px) !important;
                right: 10px !important;
                bottom: 80px !important;
            }
            
            .chat-fab-button {
                right: 10px !important;
                bottom: 10px !important;
                width: 56px !important;
                height: 56px !important;
            }
            
            .chat-buttons {
                flex-direction: column;
            }
            
            .chat-btn-primary,
            .chat-btn-secondary {
                flex: 1;
                width: 100%;
            }
        }
        
        /* Mejorar scroll del chat */
        .chat-messages {
            padding: 12px;
            background: #f8f9fa;
        }
        
        /* Mensajes del chat con mejor diseño */
        [data-testid="stChatMessage"] {
            margin-bottom: 12px !important;
            border-radius: 12px !important;
        }
        
        /* Input mejorado */
        .chat-input textarea {
            border-radius: 12px !important;
            border: 2px solid #e0e0e0 !important;
            transition: border-color 0.3s ease !important;
        }
        
        .chat-input textarea:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1) !important;
        }
        
        /* Badge del modelo */
        .model-badge {
            display: inline-block;
            padding: 4px 12px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            font-size: 12px;
            margin-top: 4px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # HTML para el botón flotante
        st.markdown("""
        <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9998;">
        </div>
        """, unsafe_allow_html=True)
        
        # Crear el chat flotante con popover en posición fija
        # Usar columns para positioning
        _, col_right = st.columns([1, 0.00001])  # Columna casi invisible a la derecha
        
        with col_right:
            with st.popover("💬", use_container_width=False):
                # Header del chat con diseño mejorado
                st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 20px; border-radius: 16px 16px 0 0; margin: -1rem -1rem 1rem -1rem;'>
                    <h3 style='color: white; margin: 0; font-size: 20px;'>🤖 streetviewer</h3>
                    <div style='display: inline-block; padding: 4px 12px; background: rgba(255,255,255,0.2); 
                                border-radius: 12px; font-size: 12px; margin-top: 8px; color: white;'>
                        ⚡ {model}
                    </div>
                </div>
                """.format(model=st.session_state.groq_model), unsafe_allow_html=True)
                
                # Botón de cerrar
                col_close1, col_close2, col_close3 = st.columns([3, 1, 0.5])
                with col_close2:
                    if st.button("❌ Cerrar", key="close_chat_popover", use_container_width=True, help="Cerrar chat"):
                        st.session_state.chat_open = False
                        st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Área de mensajes con scroll y diseño mejorado
                st.markdown("**💬 Conversación**")
                
                chat_container = st.container(height=380, border=True)
                
                with chat_container:
                    if st.session_state.chat_history:
                        for i, chat in enumerate(st.session_state.chat_history):
                            # Mensaje del usuario
                            with st.chat_message("user", avatar="👤"):
                                st.markdown(chat['user'])
                            
                            # Mensaje del asistente
                            with st.chat_message("assistant", avatar="🤖"):
                                st.markdown(chat['assistant'])
                    else:
                        st.info("👋 ¡Hola! Soy **streetviewer**, tu asistente de segmentación.\n\n**Ejemplos de preguntas:**\n• ¿Qué estrategia para Champions?\n• ¿Cuál segmento es más valioso?\n• Explica las métricas RFM")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Input de pregunta con diseño mejorado
                user_question = st.text_area(
                    "💭 Tu pregunta:",
                    placeholder="Escribe aquí tu pregunta...",
                    height=90,
                    key="chat_input_float",
                    help="Pregunta lo que necesites sobre tus segmentos"
                )
                
                # Botones con diseño responsive mejorado
                col_send, col_clear = st.columns([4, 1])
                
                with col_send:
                    send_btn = st.button(
                        "📤 Enviar", 
                        key="send_float", 
                        use_container_width=True, 
                        type="primary",
                        help="Enviar pregunta"
                    )
                
                with col_clear:
                    clear_btn = st.button(
                        "🗑️", 
                        key="clear_float", 
                        use_container_width=True, 
                        help="Limpiar todo el historial"
                    )
                
                # Procesar envío
                if send_btn and user_question:
                    with st.spinner("🤔 Pensando..."):
                        try:
                            context = get_chatbot_context(rfm)
                            messages = [
                                {"role": "system", "content": context},
                                {"role": "user", "content": user_question}
                            ]
                            
                            response = st.session_state.groq_client.chat.completions.create(
                                model=st.session_state.groq_model,
                                messages=messages,
                                temperature=0.7,
                                max_tokens=1024
                            )
                            
                            st.session_state.chat_history.append({
                                'user': user_question,
                                'assistant': response.choices[0].message.content
                            })
                            
                            st.success("✓ Respuesta recibida")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                
                elif send_btn and not user_question:
                    st.warning("⚠️ Por favor escribe una pregunta")
                
                if clear_btn:
                    st.session_state.chat_history = []
                    st.success("✓ Historial limpiado")
                    st.rerun()
    
    # ========================================================================
    # VISUALIZACIÓN DE RESULTADOS CON PESTAÑAS
    # ========================================================================
    
    st.markdown("---")
    
    # Crear pestañas principales
    tab_overview, tab_eda, tab_rfm, tab_clustering, tab_segments, tab_tree = st.tabs([
        "📊 Overview", 
        "🔍 Análisis Exploratorio",
        "📈 Análisis RFM", 
        "🎯 Clustering",
        "👥 Segmentos",
        "🌳 Árbol de Decisión"
    ])
    
    # ========================================================================
    # TAB 1: OVERVIEW - KPIs y Resumen
    # ========================================================================
    with tab_overview:
        st.subheader("📈 KPIs Principales")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_customers = len(rfm)
            st.metric(
                label="Total de Clientes",
                value=f"{total_customers:,}"
            )
        
        with col2:
            n_segments = rfm['Cluster'].nunique()
            st.metric(
                label="Número de Segmentos",
                value=n_segments
            )
        
        with col3:
            total_revenue = rfm['Monetary'].sum()
            st.metric(
                label="Ingreso Total",
                value=f"£{total_revenue:,.0f}"
            )
        
        with col4:
            avg_revenue_per_segment = rfm.groupby('Cluster')['Monetary'].sum().mean()
            st.metric(
                label="Ingreso Promedio por Segmento",
                value=f"£{avg_revenue_per_segment:,.0f}"
            )
        
        st.markdown("---")
        
        # Distribución de clientes por segmento
        st.subheader("👥 Distribución de Clientes por Segmento")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Gráfico de barras
            segment_counts = rfm['Segment'].value_counts().reset_index()
            segment_counts.columns = ['Segmento', 'Clientes']
            
            fig_bar = px.bar(
                segment_counts,
                x='Segmento',
                y='Clientes',
                color='Segmento',
                title='Número de Clientes por Segmento',
                text='Clientes',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_bar.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig_bar.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Gráfico de pastel
            fig_pie = px.pie(
                segment_counts,
                values='Clientes',
                names='Segmento',
                title='Proporción de Clientes por Segmento',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("---")
        
        # Comparación de gasto por segmento
        st.subheader("💰 Comparación de Gasto por Segmento")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Gasto total por segmento
            revenue_by_segment = rfm.groupby('Segment')['Monetary'].sum().reset_index()
            revenue_by_segment.columns = ['Segmento', 'Ingreso Total']
            revenue_by_segment = revenue_by_segment.sort_values('Ingreso Total', ascending=False)
            
            fig_revenue = px.bar(
                revenue_by_segment,
                x='Segmento',
                y='Ingreso Total',
                color='Segmento',
                title='Ingreso Total por Segmento',
                text='Ingreso Total',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_revenue.update_traces(texttemplate='£%{text:,.0f}', textposition='outside')
            fig_revenue.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        with col2:
            # Gasto promedio por segmento
            avg_revenue_by_segment = rfm.groupby('Segment')['Monetary'].mean().reset_index()
            avg_revenue_by_segment.columns = ['Segmento', 'Ingreso Promedio']
            avg_revenue_by_segment = avg_revenue_by_segment.sort_values('Ingreso Promedio', ascending=False)
            
            fig_avg = px.bar(
                avg_revenue_by_segment,
                x='Segmento',
                y='Ingreso Promedio',
                color='Segmento',
                title='Ingreso Promedio por Cliente en cada Segmento',
                text='Ingreso Promedio',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_avg.update_traces(texttemplate='£%{text:,.0f}', textposition='outside')
            fig_avg.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_avg, use_container_width=True)
        
        st.markdown("---")
        
        # Tabla resumen RFM por segmento
        st.subheader("📊 Tabla Resumen RFM por Segmento")
        
        summary_table = rfm.groupby('Segment').agg({
            'CustomerID': 'count',
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': ['mean', 'sum']
        }).round(2)
        
        summary_table.columns = ['Número de Clientes', 'Recency Promedio (días)', 
                                  'Frequency Promedio (compras)', 'Monetary Promedio (£)', 
                                  'Monetary Total (£)']
        
        summary_table = summary_table.reset_index()
        summary_table = summary_table.sort_values('Monetary Total (£)', ascending=False)
        
        # Formatear para mejor visualización
        summary_table['Monetary Promedio (£)'] = summary_table['Monetary Promedio (£)'].apply(lambda x: f'£{x:,.2f}')
        summary_table['Monetary Total (£)'] = summary_table['Monetary Total (£)'].apply(lambda x: f'£{x:,.2f}')
        
        st.dataframe(summary_table, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # TAB 2: ANÁLISIS EXPLORATORIO (EDA)
    # ========================================================================
    with tab_eda:
        st.subheader("🔍 Análisis Exploratorio de Datos")
        
        st.markdown("""
        Este análisis muestra las características principales del dataset antes del procesamiento.
        Ayuda a entender patrones, outliers y distribuciones en los datos transaccionales.
        """)
        
        if not use_preprocessed and 'df_clean' in locals():
            # Estadísticas descriptivas
            st.markdown("### 📊 Estadísticas Descriptivas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total de Transacciones", f"{len(df_clean):,}")
                st.metric("Clientes Únicos", f"{df_clean['CustomerID'].nunique():,}")
            
            with col2:
                st.metric("Productos Únicos", f"{df_clean['StockCode'].nunique():,}")
                st.metric("Países", f"{df_clean['Country'].nunique()}")
            
            st.markdown("---")
            
            # Distribuciones
            st.markdown("### 📈 Distribución de Variables Transaccionales")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_qty = px.histogram(
                    df_clean[df_clean['Quantity'] < 100],
                    x='Quantity',
                    nbins=50,
                    title='Distribución de Quantity (< 100)',
                    labels={'Quantity': 'Cantidad', 'count': 'Frecuencia'}
                )
                fig_qty.update_layout(height=400)
                st.plotly_chart(fig_qty, use_container_width=True)
            
            with col2:
                fig_price = px.histogram(
                    df_clean[df_clean['UnitPrice'] < 50],
                    x='UnitPrice',
                    nbins=50,
                    title='Distribución de UnitPrice (< £50)',
                    labels={'UnitPrice': 'Precio Unitario (£)', 'count': 'Frecuencia'}
                )
                fig_price.update_layout(height=400)
                st.plotly_chart(fig_price, use_container_width=True)
            
            # Top países
            st.markdown("### 🌍 Top 10 Países por Transacciones")
            
            top_countries = df_clean['Country'].value_counts().head(10).reset_index()
            top_countries.columns = ['País', 'Transacciones']
            
            fig_countries = px.bar(
                top_countries,
                x='País',
                y='Transacciones',
                title='Países con Más Transacciones',
                color='Transacciones',
                color_continuous_scale='Blues'
            )
            fig_countries.update_layout(height=400)
            st.plotly_chart(fig_countries, use_container_width=True)
            
        else:
            st.info("⚠️ El análisis EDA requiere cargar el archivo original. Active la opción de cargar datos desde archivo.")
    
    # ========================================================================
    # TAB 3: ANÁLISIS RFM
    # ========================================================================
    with tab_rfm:
        st.subheader("📈 Análisis RFM (Recency, Frequency, Monetary)")
        
        st.markdown("""
        **RFM** es un modelo de segmentación clásico que evalúa a los clientes en tres dimensiones:
        - **Recency**: ¿Qué tan recientemente compró? (valores bajos = mejor)
        - **Frequency**: ¿Con qué frecuencia compra? (valores altos = mejor)
        - **Monetary**: ¿Cuánto gasta? (valores altos = mejor)
        """)
        
        st.markdown("---")
        
        # Estadísticas RFM
        st.markdown("### 📊 Estadísticas RFM")
        
        rfm_stats = rfm[['Recency', 'Frequency', 'Monetary']].describe().T
        rfm_stats['min'] = rfm_stats['min'].round(2)
        rfm_stats['max'] = rfm_stats['max'].round(2)
        rfm_stats['mean'] = rfm_stats['mean'].round(2)
        rfm_stats['std'] = rfm_stats['std'].round(2)
        
        st.dataframe(rfm_stats, use_container_width=True)
        
        st.markdown("---")
        
        # Distribuciones RFM
        st.markdown("### 📈 Distribución de Métricas RFM")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_r = px.histogram(
                rfm,
                x='Recency',
                nbins=50,
                title='Distribución de Recency',
                labels={'Recency': 'Días desde última compra', 'count': 'Clientes'},
                color_discrete_sequence=['#FF6B6B']
            )
            fig_r.update_layout(height=350)
            st.plotly_chart(fig_r, use_container_width=True)
            st.caption("✓ Valores bajos = clientes recientes")
        
        with col2:
            fig_f = px.histogram(
                rfm,
                x='Frequency',
                nbins=50,
                title='Distribución de Frequency',
                labels={'Frequency': 'Número de compras', 'count': 'Clientes'},
                color_discrete_sequence=['#4ECDC4']
            )
            fig_f.update_layout(height=350)
            st.plotly_chart(fig_f, use_container_width=True)
            st.caption("✓ Valores altos = clientes frecuentes")
        
        with col3:
            fig_m = px.histogram(
                rfm,
                x='Monetary',
                nbins=50,
                title='Distribución de Monetary',
                labels={'Monetary': 'Gasto total (£)', 'count': 'Clientes'},
                color_discrete_sequence=['#45B7D1']
            )
            fig_m.update_layout(height=350)
            st.plotly_chart(fig_m, use_container_width=True)
            st.caption("✓ Valores altos = clientes valiosos")
        
        st.markdown("---")
        
        # Correlaciones RFM
        st.markdown("### 🔗 Relaciones entre Métricas RFM")
        
        corr_matrix = rfm[['Recency', 'Frequency', 'Monetary']].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect="auto",
            title='Matriz de Correlación RFM',
            color_continuous_scale='RdBu_r'
        )
        fig_corr.update_layout(height=400)
        st.plotly_chart(fig_corr, use_container_width=True)
    
    # ========================================================================
    # TAB 4: CLUSTERING
    # ========================================================================
    with tab_clustering:
        st.subheader("🎯 Análisis de Clustering K-Means")
        
        st.markdown("""
        El clustering K-Means agrupa automáticamente a los clientes con comportamientos similares.
        Analizamos diferentes valores de K para encontrar el número óptimo de segmentos.
        """)
        
        st.markdown("---")
        
        # Evaluar clustering
        if not use_preprocessed:
            scaler = StandardScaler()
            rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])
        else:
            # Si usamos datos preprocesados, crear el scaler
            scaler = StandardScaler()
            rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])
        
        K_range, inertias, silhouette_scores_list = evaluate_clustering(rfm_scaled, max_k=10)
        
        st.markdown("### 📊 Evaluación del Número Óptimo de Clusters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Método del codo
            fig_elbow = go.Figure()
            fig_elbow.add_trace(go.Scatter(
                x=list(K_range),
                y=inertias,
                mode='lines+markers',
                marker=dict(size=10, color='#FF6B6B'),
                line=dict(width=3)
            ))
            fig_elbow.update_layout(
                title='Método del Codo',
                xaxis_title='Número de Clusters (K)',
                yaxis_title='Inercia',
                height=400
            )
            st.plotly_chart(fig_elbow, use_container_width=True)
            st.caption("Buscar el 'codo' donde la inercia deja de disminuir significativamente")
        
        with col2:
            # Silhouette Score
            fig_silh = go.Figure()
            fig_silh.add_trace(go.Scatter(
                x=list(K_range),
                y=silhouette_scores_list,
                mode='lines+markers',
                marker=dict(size=10, color='#4ECDC4'),
                line=dict(width=3)
            ))
            fig_silh.update_layout(
                title='Silhouette Score por K',
                xaxis_title='Número de Clusters (K)',
                yaxis_title='Silhouette Score',
                height=400
            )
            st.plotly_chart(fig_silh, use_container_width=True)
            st.caption("Valores más altos indican mejor separación entre clusters")
        
        st.markdown("---")
        
        # Tabla de resultados
        st.markdown("### 📋 Tabla de Evaluación")
        
        eval_df = pd.DataFrame({
            'K': list(K_range),
            'Inercia': [f"{x:.2f}" for x in inertias],
            'Silhouette Score': [f"{x:.3f}" for x in silhouette_scores_list]
        })
        
        st.dataframe(eval_df, use_container_width=True, hide_index=True)
        
        st.info(f"✓ **Número óptimo seleccionado**: K = {rfm['Cluster'].nunique()} segmentos")
    
    # ========================================================================
    # TAB 5: SEGMENTOS - Visualización en Espacio RFM
    # ========================================================================
    with tab_segments:
        st.subheader("👥 Visualización de Segmentos en Espacio RFM")
        
        st.markdown("""
        Cada punto representa un cliente posicionado según sus métricas RFM.
        Los colores indican el segmento al que pertenece.
        """)
        
        st.markdown("---")
        
        subtab1, subtab2, subtab3 = st.tabs(["Recency vs Monetary", "Frequency vs Monetary", "Recency vs Frequency"])
        
        with subtab1:
            fig1 = px.scatter(
                rfm,
                x='Recency',
                y='Monetary',
                color='Segment',
                title='Segmentación: Recency vs Monetary',
                labels={'Recency': 'Recency (días)', 'Monetary': 'Monetary (£)'},
                color_discrete_sequence=px.colors.qualitative.Bold,
                hover_data=['Frequency', 'CustomerID']
            )
            fig1.update_layout(height=500)
            st.plotly_chart(fig1, use_container_width=True)
        
        with subtab2:
            fig2 = px.scatter(
                rfm,
                x='Frequency',
                y='Monetary',
                color='Segment',
                title='Segmentación: Frequency vs Monetary',
                labels={'Frequency': 'Frequency (compras)', 'Monetary': 'Monetary (£)'},
                color_discrete_sequence=px.colors.qualitative.Bold,
                hover_data=['Recency', 'CustomerID']
            )
            fig2.update_layout(height=500)
            st.plotly_chart(fig2, use_container_width=True)
        
        with subtab3:
            fig3 = px.scatter(
                rfm,
                x='Recency',
                y='Frequency',
                color='Segment',
                title='Segmentación: Recency vs Frequency',
                labels={'Recency': 'Recency (días)', 'Frequency': 'Frequency (compras)'},
                color_discrete_sequence=px.colors.qualitative.Bold,
                hover_data=['Monetary', 'CustomerID']
            )
            fig3.update_layout(height=500)
            st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("---")
        
        # Características por segmento
        st.markdown("### 📊 Características Promedio por Segmento")
        
        cluster_summary = rfm.groupby('Segment')[['Recency', 'Frequency', 'Monetary']].mean().round(2)
        cluster_summary['Clientes'] = rfm.groupby('Segment').size()
        cluster_summary = cluster_summary.reset_index()
        
        st.dataframe(cluster_summary, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # TAB 6: ÁRBOL DE DECISIÓN EXPLICATIVO
    # ========================================================================
    with tab_tree:
        st.subheader("🌳 Árbol de Decisión Explicativo")
        
        st.markdown("""
        Este árbol de decisión **NO se usa para predecir**, sino para **explicar** las reglas
        que definen cada segmento de manera interpretable para usuarios no técnicos.
        
        Cada nodo muestra:
        - La condición de decisión (ej: "Recency <= 50")
        - El segmento más común en ese grupo
        - El número de clientes
        """)
        
        st.markdown("---")
        
        # Controles interactivos para el árbol
        st.markdown("### ⚙️ Configuración del Árbol")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_depth = st.slider(
                "Profundidad Máxima",
                min_value=2,
                max_value=8,
                value=4,
                help="Mayor profundidad = más reglas detalladas pero menos interpretable"
            )
        
        with col2:
            min_samples_split = st.slider(
                "Mín. Muestras para Dividir",
                min_value=50,
                max_value=200,
                value=100,
                step=10,
                help="Número mínimo de clientes para crear una nueva regla"
            )
        
        with col3:
            min_samples_leaf = st.slider(
                "Mín. Muestras por Hoja",
                min_value=20,
                max_value=100,
                value=50,
                step=5,
                help="Número mínimo de clientes en cada segmento final"
            )
        
        st.markdown("---")
        
        # Entrenar árbol con parámetros configurables
        tree_model, X, y, y_pred = train_decision_tree(
            rfm, 
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf
        )
        
        # Información del árbol
        st.markdown("### 📊 Métricas del Modelo")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Profundidad", tree_model.get_depth())
        
        with col2:
            st.metric("Número de Hojas", tree_model.get_n_leaves())
        
        with col3:
            accuracy = accuracy_score(y, y_pred)
            st.metric("Accuracy", f"{accuracy:.1%}")
        
        with col4:
            correct_predictions = (y == y_pred).sum()
            st.metric("Predicciones Correctas", f"{correct_predictions:,}")
        
        st.markdown("---")
        
        # Matriz de Confusión
        st.markdown("### 🎯 Matriz de Confusión")
        
        st.markdown("""
        La matriz de confusión muestra qué tan bien el árbol clasifica a los clientes en cada segmento.
        - **Diagonal**: Predicciones correctas
        - **Fuera de diagonal**: Confusiones entre segmentos
        """)
        
        # Calcular matriz de confusión
        cm = confusion_matrix(y, y_pred)
        
        # Obtener nombres de segmentos ordenados
        segment_names_ordered = [rfm[rfm['Cluster'] == i]['Segment'].iloc[0] 
                                 for i in sorted(rfm['Cluster'].unique())]
        
        # Crear figura interactiva con plotly
        fig_cm = px.imshow(
            cm,
            labels=dict(x="Predicción", y="Real", color="Clientes"),
            x=segment_names_ordered,
            y=segment_names_ordered,
            color_continuous_scale='Blues',
            text_auto=True,
            aspect="auto"
        )
        
        fig_cm.update_layout(
            title='Matriz de Confusión - Clasificación de Segmentos',
            xaxis_title='Segmento Predicho',
            yaxis_title='Segmento Real',
            height=500
        )
        
        fig_cm.update_traces(
            texttemplate='%{text}',
            textfont_size=14
        )
        
        st.plotly_chart(fig_cm, use_container_width=True)
        
        # Métricas detalladas por segmento
        st.markdown("### 📋 Reporte de Clasificación por Segmento")
        
        # Crear reporte de clasificación
        report = classification_report(y, y_pred, target_names=segment_names_ordered, output_dict=True)
        report_df = pd.DataFrame(report).transpose()
        
        # Filtrar solo las filas de segmentos (sin accuracy, macro avg, weighted avg)
        segment_report = report_df.loc[segment_names_ordered].copy()
        segment_report = segment_report.round(3)
        
        # Renombrar columnas
        segment_report.columns = ['Precisión', 'Recall', 'F1-Score', 'Clientes']
        segment_report['Clientes'] = segment_report['Clientes'].astype(int)
        segment_report['Precisión'] = segment_report['Precisión'].apply(lambda x: f"{x:.1%}")
        segment_report['Recall'] = segment_report['Recall'].apply(lambda x: f"{x:.1%}")
        segment_report['F1-Score'] = segment_report['F1-Score'].apply(lambda x: f"{x:.3f}")
        
        segment_report = segment_report.reset_index()
        segment_report.columns = ['Segmento', 'Precisión', 'Recall', 'F1-Score', 'Clientes']
        
        st.dataframe(segment_report, use_container_width=True, hide_index=True)
        
        # Explicación de métricas
        with st.expander("ℹ️ ¿Qué significan estas métricas?"):
            st.markdown("""
            **Precisión**: De todos los clientes clasificados en un segmento, ¿cuántos realmente pertenecen a ese segmento?
            - Ejemplo: Si la precisión de "Champions" es 95%, significa que de todos los clientes que el modelo clasificó como Champions, el 95% realmente son Champions.
            
            **Recall (Sensibilidad)**: De todos los clientes que pertenecen a un segmento, ¿cuántos fueron correctamente identificados?
            - Ejemplo: Si el recall de "At Risk" es 85%, significa que el modelo identificó correctamente al 85% de todos los clientes que realmente están en riesgo.
            
            **F1-Score**: Promedio armónico de Precisión y Recall. Un balance entre ambas métricas.
            - Valores cercanos a 1.0 indican un modelo muy bueno para ese segmento.
            """)
        
        st.markdown("---")
        
        # Importancia de variables
        st.markdown("### 📊 Importancia de Variables")
        
        feature_importance = pd.DataFrame({
            'Variable': ['Recency', 'Frequency', 'Monetary'],
            'Importancia': tree_model.feature_importances_,
            'Porcentaje': (tree_model.feature_importances_ * 100).round(1)
        }).sort_values('Importancia', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_importance = px.bar(
                feature_importance,
                x='Variable',
                y='Importancia',
                title='Importancia de Cada Variable en la Segmentación',
                color='Importancia',
                color_continuous_scale='Viridis',
                text='Porcentaje'
            )
            fig_importance.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_importance.update_layout(height=400)
            st.plotly_chart(fig_importance, use_container_width=True)
        
        with col2:
            st.markdown("**Interpretación:**")
            for idx, row in feature_importance.iterrows():
                variable = row['Variable']
                percentage = row['Porcentaje']
                
                if percentage > 40:
                    importance_label = "🔴 Crítica"
                elif percentage > 25:
                    importance_label = "🟡 Alta"
                else:
                    importance_label = "🟢 Media"
                
                st.markdown(f"**{variable}**: {importance_label}")
                st.progress(percentage / 100)
                st.caption(f"{percentage}% de importancia")
        
        st.markdown("---")
        
        # Visualizar árbol
        st.markdown("### 🌳 Visualización del Árbol de Decisión")
        
        # Opciones de visualización
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info("""
            **Cómo leer el árbol:**
            - Cada caja muestra una regla de decisión
            - Las flechas indican el camino según si la condición es verdadera (izquierda) o falsa (derecha)
            - Las hojas finales muestran el segmento asignado
            """)
        
        with col2:
            show_impurity = st.checkbox("Mostrar Impureza", value=False, 
                                        help="Gini impurity: menor = segmento más puro")
            show_samples = st.checkbox("Mostrar % de Clientes", value=True,
                                       help="Porcentaje de clientes en cada nodo")
        
        # Crear figura del árbol con matplotlib
        from sklearn.tree import plot_tree
        
        # Ajustar tamaño según profundidad
        fig_width = max(20, tree_model.get_depth() * 4)
        fig_height = max(10, tree_model.get_depth() * 2)
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Obtener nombres de segmentos ordenados por cluster
        segment_names_ordered = [rfm[rfm['Cluster'] == i]['Segment'].iloc[0] 
                                 for i in sorted(rfm['Cluster'].unique())]
        
        plot_tree(
            tree_model,
            feature_names=['Recency', 'Frequency', 'Monetary'],
            class_names=segment_names_ordered,
            filled=True,
            rounded=True,
            fontsize=9,
            ax=ax,
            impurity=show_impurity,
            proportion=show_samples
        )
        
        plt.title('Árbol de Decisión - Reglas de Segmentación', 
                  fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        st.pyplot(fig)
        plt.close()
        
        st.markdown("---")
        
        # Extracción de reglas de decisión
        st.markdown("### 📝 Reglas de Decisión Extraídas")
        
        # Función para extraer reglas del árbol
        from sklearn.tree import _tree
        
        def extract_rules(tree_model, feature_names, class_names):
            tree_ = tree_model.tree_
            feature_name = [
                feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
                for i in tree_.feature
            ]
            
            rules = []
            
            def recurse(node, depth, conditions):
                indent = "  " * depth
                
                if tree_.feature[node] != _tree.TREE_UNDEFINED:
                    name = feature_name[node]
                    threshold = tree_.threshold[node]
                    
                    # Rama izquierda (<=)
                    left_conditions = conditions + [f"{name} ≤ {threshold:.2f}"]
                    recurse(tree_.children_left[node], depth + 1, left_conditions)
                    
                    # Rama derecha (>)
                    right_conditions = conditions + [f"{name} > {threshold:.2f}"]
                    recurse(tree_.children_right[node], depth + 1, right_conditions)
                else:
                    # Es una hoja
                    class_idx = np.argmax(tree_.value[node])
                    class_name = class_names[class_idx]
                    n_samples = tree_.n_node_samples[node]
                    
                    if len(conditions) > 0:
                        rule = " Y ".join(conditions)
                        rules.append({
                            'Regla': rule,
                            'Segmento': class_name,
                            'Clientes': n_samples
                        })
            
            recurse(0, 0, [])
            return rules
        
        rules = extract_rules(tree_model, ['Recency', 'Frequency', 'Monetary'], segment_names_ordered)
        rules_df = pd.DataFrame(rules)
        
        if len(rules_df) > 0:
            rules_df = rules_df.sort_values('Clientes', ascending=False)
            
            st.markdown("""
            Cada regla representa un camino desde la raíz del árbol hasta una hoja (segmento final).
            Estas reglas pueden usarse para clasificar manualmente nuevos clientes.
            """)
            
            # Mostrar reglas en un formato expandible por segmento
            for segment in rules_df['Segmento'].unique():
                segment_rules = rules_df[rules_df['Segmento'] == segment]
                total_customers = segment_rules['Clientes'].sum()
                
                with st.expander(f"**{segment}** ({len(segment_rules)} reglas, {total_customers:,} clientes)"):
                    for idx, row in segment_rules.iterrows():
                        st.markdown(f"**Regla {idx+1}** ({row['Clientes']:,} clientes):")
                        st.code(row['Regla'], language=None)
                        st.markdown("---")
        
        st.markdown("---")
        
        # Explicación de uso práctico
        st.markdown("### 💡 Aplicación Práctica")
        
        st.markdown("""
        **Este árbol te permite responder preguntas como:**
        - ¿Qué hace que un cliente sea clasificado como 'Champion'?
        - ¿Qué umbral de Recency separa a los clientes activos de los inactivos?
        - ¿Cuál es el nivel de Frequency que distingue a los clientes leales?
        - ¿Cómo se diferencian los segmentos en términos de reglas simples?
        
        **Ejemplo de lectura:**
        Si en el primer nodo dice "Recency <= 100":
        - Los clientes que compraron en los últimos 100 días van por la izquierda (más activos)
        - Los que no compraron en 100+ días van por la derecha (menos activos o en riesgo)
        
        **Uso para nuevos clientes:**
        Puedes usar estas reglas para clasificar manualmente nuevos clientes sin necesidad de re-entrenar el modelo.
        """)
    
    st.markdown("---")
    
    # Insights y recomendaciones
    st.subheader("💡 Insights y Recomendaciones")
    
    for segment in rfm['Segment'].unique():
        segment_data = rfm[rfm['Segment'] == segment]
        
        with st.expander(f"**{segment}** ({len(segment_data):,} clientes)"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **Características:**
                - Recency promedio: {segment_data['Recency'].mean():.0f} días
                - Frequency promedio: {segment_data['Frequency'].mean():.1f} compras
                - Monetary promedio: £{segment_data['Monetary'].mean():,.2f}
                - Contribución a ingresos: £{segment_data['Monetary'].sum():,.2f} 
                  ({(segment_data['Monetary'].sum() / rfm['Monetary'].sum() * 100):.1f}%)
                """)
                
                # Recomendaciones específicas
                if segment == 'Champions':
                    st.markdown("""
                    **🎯 Estrategia:**
                    - Programas VIP exclusivos
                    - Early access a nuevos productos
                    - Atención personalizada premium
                    - Incentivos por referidos
                    """)
                elif segment == 'Loyal Customers':
                    st.markdown("""
                    **🎯 Estrategia:**
                    - Programas de puntos y recompensas
                    - Ofertas especiales periódicas
                    - Comunicación frecuente de valor
                    - Up-selling y cross-selling
                    """)
                elif segment == 'At Risk':
                    st.markdown("""
                    **⚠️ Estrategia URGENTE:**
                    - Campañas de reactivación inmediatas
                    - Descuentos significativos
                    - Encuestas de satisfacción
                    - Win-back campaigns personalizadas
                    """)
                else:
                    st.markdown("""
                    **📈 Estrategia:**
                    - Incrementar frecuencia de compra
                    - Ofertas por volumen
                    - Recordatorios personalizados
                    - Programas de engagement
                    """)
            
            with col2:
                # Mini gráfico de distribución RFM para el segmento
                rfm_values = segment_data[['Recency', 'Frequency', 'Monetary']].mean()
                fig_mini = go.Figure(data=[
                    go.Bar(x=['R', 'F', 'M'], 
                          y=[rfm_values['Recency'], rfm_values['Frequency'], rfm_values['Monetary']],
                          marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
                ])
                fig_mini.update_layout(
                    title='Perfil RFM',
                    height=250,
                    showlegend=False,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_mini, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p><strong>Segmentación de Clientes - Retail Online Dashboard</strong></p>
        <p>Desarrollado con ❤️ usando Streamlit | Data Science Bootcamp 2025</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# EJECUTAR APLICACIÓN
# ============================================================================

if __name__ == "__main__":
    main()
