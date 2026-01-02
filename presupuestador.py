import streamlit as st
from fpdf import FPDF
import datetime

# Configuración de página con la estética de Conexión Logística Sur
st.set_page_config(page_title="Oficina Virtual - CLS", page_icon="🚚")

# Estilos CSS para profesionalizar la vista
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; background-color: #004282; color: white; border-radius: 10px; height: 3em; font-weight: bold; }
    .result-box { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 5px solid #004282; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 Conexión Logística Sur")
st.subheader("Cotizador Inteligente de Transporte - Operativa 2026")

# --- ENTRADA DE DATOS ---
with st.expander("📝 Datos del Servicio", expanded=True):
    servicio = st.selectbox("Tipo de Carga", 
                            ["Remolque de Embarcación", "Flete Estándar", "Mudanza Residencial", "Maquinaria"])
    
    col1, col2 = st.columns(2)
    with col1:
        origen = st.text_input("Ciudad de Origen", "Paysandú")
    with col2:
        destino = st.text_input("Ciudad de Destino")
        
    distancia = st.number_input("Distancia solo ida (km)", min_value=1, value=1)

# --- LÓGICA DE NEGOCIO (REGLAS DE GUSTAVO + TU INGENIERÍA) ---
distancia_total = distancia * 2  # SE COBRA IDA Y VUELTA
peaje_valor = 145
num_peajes = (distancia // 130) + 1
total_peajes = num_peajes * peaje_valor

# Variables por defecto
precio_km = 65
base = 2500
costo_trailer = 0

if servicio == "Remolque de Embarcación":
    # Regla: 150km o más -> $80 el km. Menos de 150km -> $110 el km.
    if distancia >= 150:
        precio_km = 80
    else:
        precio_km = 110
    
    base = 6500
    st.info("💡 Nota: Para lanchas hasta 27 pies. Se cobra trayecto completo (ida y vuelta).")
    
    alquiler_trailer = st.checkbox("¿Requiere alquiler de trailer de la empresa? (+$2500)")
    costo_trailer = 2500 if alquiler_trailer else 0

# Cálculo Final
total_final = base + (distancia_total * precio_km) + costo_trailer + total_peajes

# --- MOSTRAR RESULTADO ---
st.markdown("---")
st.markdown(f"""
    <div class="result-box">
        <p style="margin:0; color:#666;">PRESUPUESTO ESTIMADO 2026</p>
        <h1 style="margin:0; color:#004282;">${int(total_final):,} UYU</h1>
        <p style="font-size: 0.9em; color:#888;">*Incluye ida y vuelta, peajes y base operativa.</p>
    </div>
""", unsafe_allow_html=True)

# --- GENERADOR DE PDF Y WHATSAPP ---
def generar_pdf(total, serv, ori, dest, dist, trailer):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "CONEXION LOGISTICA SUR - OFICINA DIGITAL", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Fecha: {datetime.date.today()}", ln=True)
    pdf.cell(200, 10, f"Servicio: {serv}", ln=True)
    pdf.cell(200, 10, f"Ruta: {ori} -> {dest}", ln=True)
    pdf.cell(200, 10, f"Distancia Total (Ida/Vuelta): {dist*2} km", ln=True)
    if trailer > 0: pdf.cell(200, 10, "Incluye alquiler de trailer: SI", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, f"TOTAL: ${int(total)} UYU", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, "AVISO: Los costos son aproximados. Pueden variar segun medidas reales de la embarcacion o imprevistos en ruta.")
    return pdf.output(dest='S').encode('latin-1')

col_a, col_b = st.columns(2)

with col_a:
    pdf_bytes = generar_pdf(total_final, servicio, origen, destino, distancia, costo_trailer)
    st.download_button("📥 Descargar PDF para el Cliente", data=pdf_bytes, file_name=f"Presupuesto_CLS_{destino}.pdf")

with col_b:
    msj_wa = f"Hola, solicito el servicio de {servicio} desde {origen} hasta {destino}. El presupuesto web fue de ${int(total_final)}."
    st.link_button("💬 Confirmar por WhatsApp", f"https://wa.me/TU_NUMERO_AQUI?text={msj_wa}")
    