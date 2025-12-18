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
import pickle
from datetime import datetime, timedelta

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


# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

def main():
    """Función principal del dashboard"""
    
    # Título
    st.markdown('<p class="main-title">📊 Segmentación Inteligente de Clientes</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Dashboard de Análisis RFM y Clustering para Retail Online</p>', unsafe_allow_html=True)
    
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
    # VISUALIZACIÓN DE RESULTADOS
    # ========================================================================
    
    st.markdown("---")
    
    # KPIs principales
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
    
    # Visualización de clusters en espacio RFM
    st.subheader("🎯 Representación Visual de Clusters")
    
    tab1, tab2, tab3 = st.tabs(["Recency vs Monetary", "Frequency vs Monetary", "Recency vs Frequency"])
    
    with tab1:
        fig1 = px.scatter(
            rfm,
            x='Recency',
            y='Monetary',
            color='Segment',
            title='Segmentación: Recency vs Monetary',
            labels={'Recency': 'Recency (días)', 'Monetary': 'Monetary (£)'},
            color_discrete_sequence=px.colors.qualitative.Bold,
            hover_data=['Frequency']
        )
        fig1.update_layout(height=500)
        st.plotly_chart(fig1, use_container_width=True)
    
    with tab2:
        fig2 = px.scatter(
            rfm,
            x='Frequency',
            y='Monetary',
            color='Segment',
            title='Segmentación: Frequency vs Monetary',
            labels={'Frequency': 'Frequency (compras)', 'Monetary': 'Monetary (£)'},
            color_discrete_sequence=px.colors.qualitative.Bold,
            hover_data=['Recency']
        )
        fig2.update_layout(height=500)
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        fig3 = px.scatter(
            rfm,
            x='Recency',
            y='Frequency',
            color='Segment',
            title='Segmentación: Recency vs Frequency',
            labels={'Recency': 'Recency (días)', 'Frequency': 'Frequency (compras)'},
            color_discrete_sequence=px.colors.qualitative.Bold,
            hover_data=['Monetary']
        )
        fig3.update_layout(height=500)
        st.plotly_chart(fig3, use_container_width=True)
    
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
