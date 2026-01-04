# ... (mantené el inicio igual) ...

with st.expander("2. Detalles de la Embarcación", expanded=True):
    st.info(f"📍 Distancia estimada por ruta: **{distancia_km} km** (Solo ida)")
    col3, col4 = st.columns(2)
    with col3:
        tipo_barco = st.selectbox("Tamaño de Embarcación", ["Lancha chica", "Crucero mediano", "Embarcación Grande (Hasta 40 pies / 10 Ton)"])
        foto = st.file_uploader("📸 Subir foto de la embarcación (Verificación Obligatoria)", type=['jpg', 'png'])
    with col4:
        usa_trailer = st.toggle("Alquiler Trailer Especial (Hasta 40 pies / 10 Ton) - $8.000")
        es_premium = st.toggle("Servicio Urgente / 24hs (+15%)")
        
        # TEXTO ACLARATORIO PARA EL CLIENTE
        if es_premium:
            st.warning("""
            **¿Qué incluye el Servicio Premium?**
            * ✅ **Prioridad Total:** Despacho inmediato de la unidad.
            * ✅ **Disponibilidad 24hs:** Traslados nocturnos o en días feriados.
            * ✅ **Seguro de Carga Extendido:** Cobertura especial por urgencia.
            * ✅ **Gestión Logística Directa:** Comunicación minuto a minuto con el chofer.
            """)

# --- (En la parte del PDF, agregué esto para que también quede por escrito) ---
def crear_pdf():
    # ... (código anterior del pdf) ...
    if es_premium:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(200, 10, "INCLUYE SERVICIO PREMIUM (Prioridad 24hs y Despacho Urgente)", ln=True)
    # ... (resto del código del pdf) ...
