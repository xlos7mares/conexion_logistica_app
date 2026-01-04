import streamlit as st
from fpdf import FPDF
import datetime

# --- CONFIGURACIÓN DE LA OFICINA VIRTUAL CLS ---
st.set_page_config(page_title="Oficina Virtual CLS", page_icon="⚓", layout="wide")

# Base de datos completa de Uruguay
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
        depto_o = st.selectbox("Departamento Origen", list(UBICACIONES.keys()), index=10) # Paysandú
        ciudad_o = st.selectbox("Localidad Origen", UBICACIONES[depto_o])
        depto_d = st.selectbox("Departamento Destino", list(UBICACIONES.keys()), index=8) # Maldonado
        ciudad_d = st.selectbox("Localidad Destino", UBICACIONES[depto_d])
    
    with col2:
        distancia_ida = st.number_input("Distancia solo ida (Km)", min_value=1, value=150)
        tipo_servicio = st.selectbox("Tipo de Carga", ["Lancha hasta 27 pies", "Flete General", "Mudanza", "Maquinaria"])
        usa_trailer = st.checkbox("Incluir Alquiler de Trailer CLS (+$2.500)")
        es_premium = st.toggle("Servicio Premium (+15%)")

# --- LÓGICA GUSTAVO: Ida y Vuelta, $80/km si >= 150km ---
distancia_total = distancia_ida * 2
base_operativa = 6500
peajes = ((distancia_ida // 130) + 1) * 145

if tipo_servicio == "Lancha hasta 27 pies":
    precio_km = 80 if distancia_ida >= 150 else 110
else:
    precio_km = 75

total = base_operativa + (distancia_total * precio_km) + peajes
if usa_trailer: total += 2500
if es_premium: total *= 1.15

st.success(f"## TOTAL ESTIMADO: ${int(total):,} UYU")

# --- GENERADOR DE PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "CONEXIÓN LOGÍSTICA SUR - PRESUPUESTO", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Fecha: {datetime.date.today()}", ln=True)
    pdf.cell(200, 10, f"Ruta: {ciudad_o} a {ciudad_d}", ln=True)
    pdf.cell(200, 10, f"Servicio: {tipo_servicio}", ln=True)
    pdf.cell(200, 10, f"Distancia Total Liquidada: {distancia_total} km (Ida y Vuelta)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, f"TOTAL: ${int(total)} UYU", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, "Nota: Este presupuesto es una estimación oficial. Se cobra el trayecto completo desde la salida hasta el regreso a la base.")
    return pdf.output(dest='S').encode('latin-1')

# --- BOTONES ---
st.download_button("📥 DESCARGAR PRESUPUESTO PDF", data=crear_pdf(), file_name=f"Presupuesto_CLS_{ciudad_d}.pdf")
st.link_button("🟢 CONSULTAR POR WHATSAPP", f"https://wa.me/59899123456?text=Hola, quiero reservar flete de {ciudad_o} a {ciudad_d}.")
