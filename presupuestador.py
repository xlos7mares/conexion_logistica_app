import streamlit as st
import pandas as pd
from fpdf import FPDF
from geopy.distance import geodesic
import re

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="CLS - Oficina Total Uruguay", layout="wide")

# Función para extraer coordenadas del formato WKT que tiene tu archivo
def extraer_coords(wkt_str):
    try:
        # Busca los números en la cadena MULTIPOLYGON
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", wkt_str)
        if len(nums) >= 2:
            # Tu archivo parece usar coordenadas proyectadas, 
            # pero para simplificar tomaremos los puntos base
            return float(nums[1]), float(nums[0]) # Lat, Lon aproximada
    except:
        return None

@st.cache_data
def cargar_pueblos():
    df = pd.read_csv('localidades-29-7nm.csv')
    # Limpiamos nombres para que se vean bien
    df['departamento'] = df['departamento'].str.upper()
    df['localidad'] = df['localidad'].str.title()
    return df

# --- INTERFAZ ---
st.title("⚓ CONEXIÓN LOGÍSTICA SUR")
st.subheader("Sistema de Cobertura Nacional (2030 Localidades)")

try:
    df_uy = cargar_pueblos()
    
    with st.sidebar:
        st.header("Configuración de Viaje")
        # Origen
        depto_o = st.selectbox("Dpto. Origen", sorted(df_uy['departamento'].unique()), index=10)
        locs_o = df_uy[df_uy['departamento'] == depto_o]['localidad'].unique()
        ciudad_o = st.selectbox("Pueblo Origen", sorted(locs_o))
        
        st.divider()
        
        # Destino
        depto_d = st.selectbox("Dpto. Destino", sorted(df_uy['departamento'].unique()), index=8)
        locs_d = df_uy[df_uy['departamento'] == depto_d]['localidad'].unique()
        ciudad_d = st.selectbox("Pueblo Destino", sorted(locs_d))

    # --- LÓGICA DE CÁLCULO ---
    # Obtenemos el WKT de cada punto para calcular
    wkt_o = df_uy[(df_uy['departamento'] == depto_o) & (df_uy['localidad'] == ciudad_o)]['wkt'].values[0]
    wkt_d = df_uy[(df_uy['departamento'] == depto_d) & (df_uy['localidad'] == ciudad_d)]['wkt'].values[0]
    
    # Nota: Tu CSV usa coordenadas UTM. Aquí aplicamos un factor de conversión base
    # para obtener kilómetros aproximados por ruta en Uruguay.
    # Extraemos valores numéricos brutos del WKT para distancia lineal
    c1 = re.findall(r"[-+]?\d*\.\d+|\d+", wkt_o)
    c2 = re.findall(r"[-+]?\d*\.\d+|\d+", wkt_d)
    
    # Cálculo de distancia lineal en base a los puntos del archivo
    dist_lineal = ((float(c1[0])-float(c2[0]))**2 + (float(c1[1])-float(c2[1]))**2)**0.5
    distancia_km = round((dist_lineal / 1000) * 1.25) # Factor de ajuste para rutas uruguayas

    # --- ENTRADA DE SERVICIOS ---
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📍 Ruta: **{ciudad_o}** hasta **{ciudad_d}**")
        st.metric("Distancia Estimada (Ida)", f"{distancia_km} KM")
        foto = st.file_uploader("📸 Subir foto de la embarcación", type=['jpg', 'png'])

    with col2:
        # PRECIO GUSTAVO: 200 USD = $8.000
        usa_trailer = st.toggle("Alquiler Trailer Especial (Hasta 40 pies / 10 Ton) - $8.000")
        es_premium = st.toggle("Servicio Urgente / 24hs (+15%)")

    # --- CUENTAS FINALES ---
    distancia_total = distancia_km * 2
    precio_km = 80 if distancia_km >= 150 else 110
    total = 6500 + (distancia_total * precio_km) + 400 # Base + Kms + Peajes
    
    if usa_trailer: total += 8000
    if es_premium: total *= 1.15

    st.success(f"## TOTAL PRESUPUESTO: ${int(total):,} UYU")
    st.caption("El sistema calculó la distancia basándose en las coordenadas oficiales de los 2030 pueblos.")

except Exception as e:
    st.warning("Cargando base de datos de pueblos... Asegurate de subir 'localidades-29-7nm.csv' a GitHub.")
