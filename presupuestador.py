import streamlit as st
import pandas as pd
from fpdf import FPDF
import re

# --- CONFIGURACIÓN DE LA OFICINA VIRTUAL CLS ---
st.set_page_config(page_title="Cotizador CLS 2026", page_icon="⚓", layout="wide")

@st.cache_data
def cargar_pueblos():
    try:
        df = pd.read_csv('localidades-29-7nm.csv')
        df['departamento'] = df['departamento'].str.upper()
        df['localidad'] = df['localidad'].str.title()
        return df
    except:
        st.error("⚠️ Error: No se encontró el archivo 'localidades-29-7nm.csv'. Por favor, asegúrate de subirlo a tu repositorio de GitHub.")
        st.stop()

# --- TÍTULO INSTITUCIONAL (Sin nombre personal) ---
st.title("⚓ CONEXIÓN LOGÍSTICA SUR")
st.subheader("Cotizador Oficial de Servicios 2026")

df_uy = cargar_pueblos()

# --- SELECCIÓN DE RUTA ---
with st.expander("1. Origen y Destino (Cobertura Nacional)", expanded=True):
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

# --- DETALLES DEL SERVICIO ---
with st.expander("2. Detalles de la Embarcación y Adicionales", expanded=True):
    st.info(f"📍 Distancia estimada: **{distancia_km} km** (Solo ida)")
    col1, col2 = st.columns(2)
    with col1:
        tipo_barco = st.selectbox("Tamaño de Embarcación", ["Lancha chica", "Crucero mediano", "Embarcación Grande (Hasta 40 pies / 10 Ton)"])
        foto = st.file_uploader("📸 Subir foto para verificación de medidas (Obligatorio)", type=['jpg', 'png'])
    with col2:
        usa_trailer = st.toggle("Alquiler Trailer Especial (Hasta 40 pies / 10 Ton) - $8.000")
        es_premium = st.toggle("Servicio Premium / 24hs (+15%)")
        
        if es_premium:
            st.warning("""
            **¿Qué incluye el Servicio Premium?**
            * ✅ **Prioridad Total:** Despacho inmediato.
            * ✅ **Disponibilidad 24hs:** Traslados nocturnos o en feriados.
            * ✅ **Gestión Directa:** Seguimiento en tiempo real del traslado.
            """)

# --- CÁLCULO DE COSTOS ---
distancia_total = distancia_km * 2
base_operativa = 6500
peajes = ((distancia_km // 130) + 1) * 145
precio_km = 80 if distancia_km >= 150 else 110

total = base_operativa + (distancia_total * precio_km) + peajes
if usa_trailer: total += 8000
if es_premium: total *= 1.15

# --- RESULTADOS ---
st.success(f"### TOTAL ESTIMADO: ${int(total):,} UYU")
st.caption(f"Incluye trayecto completo (Ida y Vuelta) y peajes estimados.")

# --- GENERADOR DE PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "CONEXIÓN LOGÍSTICA SUR - COTIZACIÓN", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Ruta: {ciudad_o} ({depto_o}) a {ciudad_d} ({depto_d})", ln=True)
    pdf.cell(200, 10, f"Embarcación: {tipo_barco}", ln=True)
    if usa_trailer: pdf.cell(200, 10, "Servicio: Incluye Trailer Especial (Hasta 40 pies)", ln=True)
    if es_premium: pdf.cell(200, 10, "Incluye: Servicio Premium (Atención 24hs y Prioridad)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, f"TOTAL: ${int(total)} UYU", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, "Nota: El alquiler del trailer es de hasta 200 USD ($8.000) por 24hs. Precios sujetos a verificación de medidas.")
    return pdf.output(dest='S').encode('latin-1')

st.download_button("📥 DESCARGAR COTIZACIÓN PDF", data=crear_pdf(), file_name=f"Cotizacion_CLS_{ciudad_d}.pdf")
