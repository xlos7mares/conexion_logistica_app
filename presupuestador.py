import streamlit as st
from fpdf import FPDF
import datetime

# --- CONFIGURACIÓN DE LA OFICINA VIRTUAL CLS ---
st.set_page_config(page_title="Oficina Virtual CLS", page_icon="⚓", layout="wide")

# Base de datos completa de Uruguay (19 departamentos)
UBICACIONES = {
    "Artigas": ["Artigas Ciudad", "Bella Unión", "Baltasar Brum"],
    "Canelones": ["Canelones Ciudad", "Santa Lucía", "Pando", "Atlántida", "Ciudad de la Costa", "Las Piedras"],
    "Cerro Largo": ["Melo", "Río Branco"],
    "Colonia": ["Colonia del Sacramento", "Carmelo", "Nueva Helvecia", "Rosario", "Nueva Palmira"],
    "Durazno": ["Durazno Ciudad", "Sarandí del Yí"],
    "Flores": ["Trinidad"],
    "Florida": ["Florida Ciudad", "Sarandí Grande"],
    "Lavalleja": ["Minas", "José Pedro Varela"],
    "Maldonado": ["Maldonado Ciudad", "Punta del Este", "Piriápolis", "San Carlos", "Pan de Azúcar", "José Ignacio"],
    "Montevideo": ["Centro", "Carrasco", "Paso de la Arena", "Pocitos", "Prado", "Cerro"],
    "Paysandú": ["Paysandú Ciudad", "Guichón", "Quebracho", "Piedras Coloradas"],
    "Río Negro": ["Fray Bentos", "Young"],
    "Rivera": ["Rivera Ciudad", "Vichadero"],
    "Rocha": ["Rocha Ciudad", "Chuy", "La Paloma", "Castillos", "Punta del Diablo"],
    "Salto": ["Salto Ciudad", "Constitución"],
    "San José": ["San José de Mayo", "Libertad", "Ciudad del Plata"],
    "Soriano": ["Mercedes", "Dolores", "Cardona"],
    "Tacuarembó": ["Tacuarembó Ciudad", "Paso de los Toros", "San Gregorio de Polanco"],
    "Treinta y Tres": ["Treinta y Tres Ciudad", "Vergara"]
}

st.title("⚓ CONEXIÓN LOGÍSTICA SUR")
st.subheader("Oficina Digital 2026 - Gestión: Leonardo Olivera")

# --- ENTRADA DE DATOS ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        depto_o = st.selectbox("Departamento Origen", list(UBICACIONES.keys()), index=10)
        ciudad_o = st.selectbox("Localidad Origen", UBICACIONES[depto_o])
        depto_d = st.selectbox("Departamento Destino", list(UBICACIONES.keys()), index=8)
        ciudad_d = st.selectbox("Localidad Destino", UBICACIONES[depto_d])
    
    with col2:
        distancia_ida = st.number_input("Distancia solo ida (Km)", min_value=1, value=150)
        tipo_servicio = st.selectbox("Tipo de Embarcación", ["Hasta 27 pies", "Grande (28 a 40 pies)", "Maquinaria Pesada"])
        # ACTUALIZACIÓN: Trailer para barcos grandes $8000 (aprox 200 USD)
        usa_trailer = st.checkbox("Alquiler Trailer Especial (Hasta 40 pies / 10 Ton) - $8.000")
        es_premium = st.toggle("Servicio Especial 24hs / Urgente (+15%)")

# --- LÓGICA DE COSTOS ---
distancia_total = distancia_ida * 2
base_operativa = 6500
peajes = ((distancia_ida // 130) + 1) * 145

# Precio por KM según distancia (Regla de los 150km)
precio_km = 80 if distancia_ida >= 150 else 110

total = base_operativa + (distancia_total * precio_km) + peajes

if usa_trailer: 
    total += 8000 # El nuevo costo de $8000

if es_premium: 
    total *= 1.15

st.success(f"## TOTAL ESTIMADO: ${int(total):,} UYU")
st.info(f"Incluye trayecto completo (Ida y Vuelta: {distancia_total} km)")

# --- GENERADOR DE PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "CONEXIÓN LOGÍSTICA SUR - PRESUPUESTO OFICIAL", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Ruta: {ciudad_o} a {ciudad_d}", ln=True)
    pdf.cell(200, 10, f"Detalle: {tipo_servicio} con Trailer Especial" if usa_trailer else f"Detalle: {tipo_servicio}", ln=True)
    pdf.cell(200, 10, f"Distancia Total (Retorno incluido): {distancia_total} km", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, f"TOTAL A PAGAR: ${int(total)} UYU", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, "Nota: El alquiler del trailer cubre hasta 24 horas de servicio y embarcaciones de hasta 10 toneladas. Se requiere declaración exacta de medidas.")
    return pdf.output(dest='S').encode('latin-1')

st.download_button("📥 DESCARGAR PRESUPUESTO PDF", data=crear_pdf(), file_name=f"Presupuesto_CLS_{ciudad_d}.pdf")
