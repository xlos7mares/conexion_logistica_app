import streamlit as st
import pandas as pd
from fpdf import FPDF
import re
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cotizador CLS 2026", layout="wide")

@st.cache_data
def cargar_pueblos():
    try:
        # Lee el archivo de los 2030 pueblos
        df = pd.read_csv('localidades-29-7nm.csv')
        df['departamento'] = df['departamento'].str.upper()
        df['localidad'] = df['localidad'].str.title()
        return df
    except Exception as e:
        st.error(f"⚠️ Error: No se encuentra el archivo de datos en GitHub.")
        st.stop()

st.title("⚓ CONEXIÓN LOGÍSTICA SUR")
st.subheader("Cotizador Oficial de Servicios 2026")

df_uy = cargar_pueblos()

# --- SELECCIÓN DE RUTA ---
with st.expander("1. Origen y Destino", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        depto_o = st.selectbox("Dpto. Origen", sorted(df_uy['departamento'].unique()), index=10)
        locs_o = df_uy[df_uy['departamento'] == depto_o]['localidad'].unique()
        ciudad_o = st.selectbox("Pueblo Origen", sorted(locs_o))
    with col_b:
        depto_d = st.selectbox("Dpto. Destino", sorted(df_uy['departamento'].unique()), index=8)
        locs_d = df_uy[df_uy['departamento'] == depto_d]['localidad'].unique()
        ciudad_d = st.selectbox("Pueblo Destino", sorted(locs_d))

# --- LÓGICA DE DISTANCIA ---
wkt_o = df_uy[(df_uy['departamento'] == depto_o) & (df_uy['localidad'] == ciudad_o)]['wkt'].values[0]
wkt_d = df_uy[(df_uy['departamento'] == depto_d) & (df_uy['localidad'] == ciudad_d)]['wkt'].values[0]
c1 = re.findall(r"[-+]?\d*\.\d+|\d+", wkt_o)
c2 = re.findall(r"[-+]?\d*\.\d+|\d+", wkt_d)
dist_lineal = ((float(c1[0])-float(c2[0]))**2 + (float(c1[1])-float(c2[1]))**2)**0.5
distancia_km = round((dist_lineal / 1000) * 1.25)

# --- SERVICIOS ACTUALIZADOS ---
with st.expander("2. Información de la Embarcación", expanded=True):
    st.info(f"📍 Distancia estimada: **{distancia_km} km**")
    foto = st.file_uploader("📸 Subir foto para verificación", type=['jpg', 'png', 'jpeg'])
    col1, col2 = st.columns(2)
    with col1:
        # CAMBIO: Ahora dice 40 pies
        tipo_barco = st.selectbox("Categoría", ["Lancha chica", "Embarcación Grande (Hasta 40 pies / 10 Ton)"])
    with col2:
        # CAMBIO: Ahora dice $8.000 (200 USD)
        usa_trailer = st.toggle("Alquiler Trailer Especial (Hasta 40 pies) - $8.000")
        es_premium = st.toggle("Servicio Premium / 24hs (+15%)")

# --- COSTOS ---
distancia_total = distancia_km * 2
precio_km = 80 if distancia_km >= 150 else 110
total = 6500 + (distancia_total * precio_km) + 400
if usa_trailer: total += 8000
if es_premium: total *= 1.15

st.success(f"### TOTAL ESTIMADO: ${int(total):,} UYU")

# WHATSAPP A LEONARDO (+598 99417716)
mensaje = f"Hola Leonardo, solicito presupuesto: \n📍 Ruta: {ciudad_o} a {ciudad_d} \n💰 Total: ${int(total):,} UYU."
whatsapp_link = f"https://wa.me/59899417716?text={urllib.parse.quote(mensaje)}"

st.link_button("📲 ENVIAR A MI WHATSAPP (LEONARDO)", whatsapp_link, type="primary")
