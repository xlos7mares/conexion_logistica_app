import streamlit as st
import pandas as pd
from fpdf import FPDF
import re
import urllib.parse

# --- CONFIGURACIÓN DE LA OFICINA VIRTUAL CLS ---
st.set_page_config(page_title="Cotizador CLS 2026", page_icon="⚓", layout="wide")

@st.cache_data
def cargar_pueblos():
    try:
        # Esto lee el archivo de los 2030 pueblos que subiste
        df = pd.read_csv('localidades-29-7nm.csv')
        df['departamento'] = df['departamento'].str.upper()
        df['localidad'] = df['localidad'].str.title()
        return df
    except:
        st.error("⚠️ Error: Suba el archivo 'localidades-29-7nm.csv' a GitHub.")
        st.stop()

# TÍTULO INSTITUCIONAL (Sin nombre personal como pediste)
st.title("⚓ CONEXIÓN LOGÍSTICA SUR")
st.subheader("Cotizador Oficial de Servicios 2026")

df_uy = cargar_pueblos()

# --- SELECCIÓN DE RUTA (2030 Localidades) ---
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

# --- LÓGICA DE DISTANCIA AUTOMÁTICA ---
wkt_o = df_uy[(df_uy['departamento'] == depto_o) & (df_uy['localidad'] == ciudad_o)]['wkt'].values[0]
wkt_d = df_uy[(df_uy['departamento'] == depto_d) & (df_uy['localidad'] == ciudad_d)]['wkt'].values[0]
c1 = re.findall(r"[-+]?\d*\.\d+|\d+", wkt_o)
c2 = re.findall(r"[-+]?\d*\.\d+|\d+", wkt_d)
dist_lineal = ((float(c1[0])-float(c2[0]))**2 + (float(c1[1])-float(c2[1]))**2)**0.5
distancia_km = round((dist_lineal / 1000) * 1.25)

# --- DETALLES DEL SERVICIO Y FOTO ---
with st.expander("2. Información de la Embarcación", expanded=True):
    st.write("### 📸 Verificación de Medidas")
    foto = st.file_uploader("Suba la foto de la embarcación aquí", type=['jpg', 'png', 'jpeg'])
    
    col1, col2 = st.columns(2)
    with col1:
        # ACTUALIZACIÓN: Lanchas de hasta 40 pies
        tipo_barco = st.selectbox("Categoría", ["Lancha chica", "Embarcación Grande (Hasta 40 pies / 10 Ton)"])
    with col2:
        # ACTUALIZACIÓN: Trailer a $8.000 (200 USD)
        usa_trailer = st.toggle("Alquiler Trailer Especial (Hasta 40 pies) - $8.000")
        es_premium = st.toggle("Servicio Premium / 24hs (+15%)")
        
        if es_premium:
            st.warning("Incluye: Prioridad total, traslados nocturnos o feriados.")

# --- CÁLCULO DE COSTOS ---
distancia_total = distancia_km * 2
base_operativa = 6500
peajes = ((distancia_km // 130) + 1) * 145
precio_km = 80 if distancia_km >= 150 else 110

total = base_operativa + (distancia_total * precio_km) + peajes
if usa_trailer: total += 8000
if es_premium: total *= 1.15

# --- RESULTADOS Y WHATSAPP ---
st.success(f"### TOTAL ESTIMADO: ${int(total):,} UYU")

# MENSAJE A TU WHATSAPP (+598 99417716)
mensaje = f"Hola Leonardo, envío presupuesto: \n📍 Ruta: {ciudad_o} a {ciudad_d} \n🚢 Barco: {tipo_barco} \n💰 Total: ${int(total):,} UYU."
mensaje_url = urllib.parse.quote(mensaje)
whatsapp_link = f"https://wa.me/59899417716?text={mensaje_url}"

col_pdf, col_wa = st.columns(2)
with col_wa:
    st.link_button("📲 ENVIAR A LEONARDO POR WHATSAPP", whatsapp_link, type="primary")

with col_pdf:
    def crear_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "CONEXIÓN LOGÍSTICA SUR - COTIZACIÓN", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.ln(10)
        pdf.cell(200, 10, f"Ruta: {ciudad_o} a {ciudad_d} ({distancia_km} km)", ln=True)
        pdf.cell(200, 10, f"Trailer Especial: {'Sí' if usa_trailer else 'No'}", ln=True)
        pdf.cell(200, 10, f"TOTAL: ${int(total)} UYU", ln=True)
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 DESCARGAR PDF", data=crear_pdf(), file_name="Cotizacion_CLS.pdf")
