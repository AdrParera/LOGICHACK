import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Inicializar sesión
if 'data_loaded' not in st.session_state:
    
    st.session_state.df_main = None
    st.session_state.file_name = None
def load_excel_file(uploaded_file):
    """Cargar y procesar archivo Excel"""
    try:
        # Leer todas las hojas disponibles
        excel_file = pd.ExcelFile(uploaded_file)
        sheets_dict = {}
        
        for sheet_name in excel_file.sheet_names:
            sheets_dict[sheet_name] = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        
        return sheets_dict
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
        return None

def analyze_inventory(df):
    """Analizar datos de inventario"""
    analysis = {}
    
    # Validar columnas necesarias
    required_columns = ['sede', 'producto', 'cantidad', 'precio_unitario']
    
    # Buscar columnas con nombres similares
    col_mapping = {}
    df_cols_lower = [col.lower() for col in df.columns]
    
    if any('sede' in col.lower() for col in df_cols_lower):
        col_mapping['sede'] = [col for col in df.columns if 'sede' in col.lower()][0]
    if any('producto' in col.lower() for col in df_cols_lower):
        col_mapping['producto'] = [col for col in df.columns if 'producto' in col.lower()][0]
    if any('cantidad' in col.lower() for col in df_cols_lower):
        col_mapping['cantidad'] = [col for col in df.columns if 'cantidad' in col.lower()][0]
    if any('precio' in col.lower() for col in df_cols_lower):
        col_mapping['precio' ] = [col for col in df.columns if 'precio' in col.lower()][0]
    
    return df, col_mapping

def crear_interfaz_principal():
    """Crear interfaz principal"""
    
    # Header de bienvenida
    st.markdown("""
        <div class="welcome-header">
            <h1>📦 Sistema de Gestión de Inventarios</h1>
            <p>¡Bienvenido! Ingresa tus archivos aquí:</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sección de carga de archivos
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "📁 Selecciona tu archivo Excel",
            type=['xlsx', 'xls', 'csv'],
            help="Carga archivos Excel o CSV con datos de inventario"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    return uploaded_file

def mostrar_dashboard(sheets_dict):
    """Mostrar dashboard con análisis"""
    
    st.success("✅ Archivo cargado correctamente")
    
    # Pestaña para seleccionar hoja
    tab_list = list(sheets_dict.keys())
    selected_sheet = st.selectbox("Selecciona la hoja a analizar:", tab_list)
    
    df = sheets_dict[selected_sheet]
    
    if df is None or df.empty:
        st.warning("El archivo no contiene datos válidos")
        return
    
    # Mostrar vista previa
    with st.expander("👁️ Vista previa de datos", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
        st.info(f"📊 Total de registros: {len(df)}")
    
    # Análisis por sede
    st.markdown("---")
    st.subheader("📍 Análisis por Sede")
    
    # Buscar columna sede
    col_sede = None
    for col in df.columns:
        if 'sede' in col.lower():
            col_sede = col
            break
    
    if col_sede:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sedes = df[col_sede].unique()
            st.metric("Total de Sedes", len(sedes))
        
        with col2:
            st.metric("Total de Registros", len(df))
        
        with col3:
            st.metric("Columnas de Datos", len(df.columns))
        
        # Gráfico de distribución por sede
        if col_sede in df.columns:
            fig = px.bar(
                df[col_sede].value_counts().reset_index(),
                x=col_sede,
                y='count',
                title="📊 Cantidad de Productos por Sede",
                labels={col_sede: "Sede", 'count': "Cantidad"},
                color_discrete_sequence=['#3b82f6']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Análisis de productos
    st.markdown("---")
    st.subheader("🛍️ Análisis de Productos")
    
    col_producto = None
    for col in df.columns:
        if 'producto' in col.lower():
            col_producto = col
            break
    
    if col_producto:
        top_productos = df[col_producto].value_counts().head(10)
        
        fig = px.bar(
            top_productos.reset_index(),
            x=col_producto,
            y='count',
            title="🏆 Top 10 Productos Más Comunes",
            labels={col_producto: "Producto", 'count': "Cantidad"},
            color_discrete_sequence=['#10b981']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Análisis de cantidades/stock
    st.markdown("---")
    st.subheader("📦 Análisis de Stock")
    
    col_cantidad = None
    for col in df.columns:
        if 'cantidad' in col.lower():
            col_cantidad = col
            break
    
    if col_cantidad and df[col_cantidad].dtype in ['int64', 'float64']:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Stock Total", f"{df[col_cantidad].sum():,.0f}")
        with col2:
            st.metric("Stock Promedio", f"{df[col_cantidad].mean():,.0f}")
        with col3:
            st.metric("Stock Máximo", f"{df[col_cantidad].max():,.0f}")
        with col4:
            st.metric("Stock Mínimo", f"{df[col_cantidad].min():,.0f}")
        
        # Histograma de distribución
        fig = px.histogram(
            df,
            x=col_cantidad,
            nbins=30,
            title="📈 Distribución de Stock",
            labels={col_cantidad: "Cantidad"},
            color_discrete_sequence=['#f59e0b']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Comparativa de sedes
    if col_sede and col_cantidad:
        st.markdown("---")
        st.subheader("🏢 Comparativa de Sedes")
        
        comparativa = df.groupby(col_sede)[col_cantidad].agg(['sum', 'mean', 'count']).reset_index()
        comparativa.columns = [col_sede, 'Stock Total', 'Stock Promedio', 'Cantidad Productos']
        
        # Encontrar sedes con más y menos ventas
        sede_mas_ventas = comparativa.loc[comparativa['Stock Total'].idxmax()]
        sede_menos_ventas = comparativa.loc[comparativa['Stock Total'].idxmin()]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="card">
                    <h4>📈 Sede con Más Stock</h4>
                    <h3>{sede_mas_ventas[col_sede]}</h3>
                    <p>Stock: {sede_mas_ventas['Stock Total']:,.0f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="card">
                    <h4>📉 Sede con Menos Stock</h4>
                    <h3>{sede_menos_ventas[col_sede]}</h3>
                    <p>Stock: {sede_menos_ventas['Stock Total']:,.0f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="card">
                    <h4>📊 Total de Sedes</h4>
                    <h3>{len(comparativa)}</h3>
                    <p>Stock Combinado: {comparativa['Stock Total'].sum():,.0f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Tabla comparativa
        st.dataframe(comparativa, use_container_width=True)
        
        # Gráfico de comparativa
        fig = px.bar(
            comparativa,
            x=col_sede,
            y='Stock Total',
            title="📊 Stock Total por Sede",
            labels={col_sede: "Sede", 'Stock Total': "Stock Total"},
            color='Stock Total',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de comparativa - Stock Promedio
        fig2 = px.line(
            comparativa,
            x=col_sede,
            y='Stock Promedio',
            markers=True,
            title="📈 Stock Promedio por Sede",
            labels={col_sede: "Sede", 'Stock Promedio': "Stock Promedio"}
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Tabla de datos completa
    st.markdown("---")
    st.subheader("📋 Datos Completos")
    
    if st.checkbox("Ver todos los datos"):
        st.dataframe(df, use_container_width=True)
        
        # Opción para descargar
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Descargar datos en CSV",
            data=csv,
            file_name="datos_inventario.csv",
            mime="text/csv"
        )

def main():
    """Función principal"""

    # Configurar página
    st.set_page_config(
        page_title="Sistema de Gestión de Inventarios",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # CSS personalizado para diseño elegante
    st.markdown("""
        <style>
        * {
            margin: 0;
            padding: 0;
        }

        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }

        .stApp {
            background-color: #ffffff;
        }

        [data-testid="stHeader"] {
            background-color: #1e3a8a;
            color: white;
        }

        .welcome-header {
            text-align: center;
            padding: 30px 0;
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 30px;
        }

        .welcome-header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .welcome-header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .card {
            background-color: #f8fafc;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 10px 0;
            border-left: 4px solid #3b82f6;
        }

        .metric-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            border-top: 4px solid #3b82f6;
        }

        .file-uploader {
            border: 2px dashed #3b82f6;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            background-color: #f0f4ff;
        }
        </style>
    """, unsafe_allow_html=True)

    # Crear interfaz de carga
    uploaded_file = crear_interfaz_principal()
    
    # Procesar archivo
    if uploaded_file is not None:
        st.session_state.file_name = uploaded_file.name
        
        # Mostrar indicador de carga
        with st.spinner("🔄 Analizando archivo..."):
            sheets_dict = load_excel_file(uploaded_file)
        
        if sheets_dict:
            st.session_state.data_loaded = True
            mostrar_dashboard(sheets_dict)
    
    # Si no hay archivo, mostrar instrucciones
    if not st.session_state.data_loaded and uploaded_file is None:
        st.markdown("""
            <div style='text-align: center; padding: 50px; color: #666;'>
                <h3>📚 Instrucciones</h3>
                <p><b>Tu archivo Excel debe contener las siguientes columnas:</b></p>
                <ul style='text-align: left; display: inline-block;'>
                    <li><b>Sede</b> - Nombre de la ubicación</li>
                    <li><b>Producto</b> - Nombre del producto</li>
                    <li><b>Cantidad</b> - Stock disponible</li>
                    <li><b>Precio_Unitario</b> - Precio de cada unidad</li>
                    <li><b>Fecha_Entrada</b> - (Opcional) Fecha de entrada</li>
                </ul>
                <br>
                <p>💡 El programa detectará automáticamente las columnas similares</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #999; font-size: 0.9em;'>
            <p>Sistema de Gestión de Inventarios © 2025 | Desarrollado con ❤️</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
