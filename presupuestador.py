import streamlit as st
import pandas as pd
import re
import math
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CLS - Cotizador Oficial", page_icon="🚛", layout="centered")

# --- VALORES DEL DÍA (Ajustar manualmente cada mañana) ---
TARIFA_MUDANZA_KM = 55.0  
TARIFA_BARCO_KM = 80.0    
EXTRA_TRAILER_USD = 200.0   # U$S 200 Dólares Americanos
COTIZACION_BROU_MAX = 42.85  # Cotización Venta del día (BROU)

# --- DISEÑO RESPONSIVO (LOGO) ---
st.markdown(
    """
    <style>
    .header-container { text-align: center; font-family: sans-serif; padding-bottom: 10px; }
    .anchor-top { font-size: 50px; margin-bottom: -15px; }
    .logo-row { display: flex; align-items: center; justify-content: center; gap: 10px; flex-wrap: nowrap; }
    .side-icon { font-size: clamp(30px, 6vw, 50px); }
    .title-text { 
        color: #01579b; font-weight: 800; margin: 0;
        font-size: clamp(16px, 4.5vw, 38px); 
        white-space: nowrap; text-transform: uppercase;
    }
    .price-box {
        background-color: #f1f8e9; padding: 25px; border-radius: 15px;
        text-align: center; border: 2px solid #2e7d32; margin-top: 20px;
    }
    </style>
    <div class="header-container">
        <div class="anchor-top">⚓</div>
        <div class="logo-row">
            <span class="side-icon">🚤</span>
            <h1 class="title-text">CONEXIÓN LOGÍSTICA SUR</h1>
            <span class="side-icon">🚛</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv('localidades-29-7nm (1).csv')
        def get_centroid(wkt):
            c = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", wkt)]
            return (sum(c[0::2])/len(c[0::2]), sum(c[1::2])/len(c[1::2])) if c else (0,0)
        df['cx'], df['cy'] = zip(*df['wkt'].apply(get_centroid))
        return df
    except: return None

df_localidades = cargar_datos()

if df_localidades is not None:
    # 1. Rubro
    rubro = st.radio("### 🛠️ ¿Qué desea cotizar?", ["📦 Mudanzas, Mercaderías u Objetos", "🚤 Embarcaciones (Lanchas/Cruceros)"], horizontal=True)

    # 2. Origen y Destino
    col1, col2 = st.columns(2)
    with col1:
        d_o = st.selectbox("Dpto. Origen:", sorted(df_localidades['departamento'].unique()))
        l_o = st.selectbox("Ciudad Origen:", sorted(df_localidades[df_localidades['departamento'] == d_o]['localidad'].unique()))
    with col2:
        d_d = st.selectbox("Dpto. Destino:", sorted(df_localidades['departamento'].unique()))
        l_d = st.selectbox("Ciudad Destino:", sorted(df_localidades[df_localidades['departamento'] == d_d]['localidad'].unique()))

    # 3. Lógica de Carga Pesada (Suma de U$S 200)
    extra_pesos_brou = 0.0
    es_pesada = False
    
    if "🚤" in rubro:
        tipo_b = st.selectbox("Detalle de la Embarcación:", 
                              ["Lancha chica (Estándar)", "Crucero mediano", "Embarcación Grande (Carga Pesada + Tráiler)"])
        
        if "Carga Pesada" in tipo_b:
            es_pesada = True
            # Convertimos los 200 Dólares a Pesos Uruguayos según BROU
            extra_pesos_brou = EXTRA_TRAILER_USD * COTIZACION_BROU_MAX
            st.warning(f"🔔 Costo Adicional: **U$S {EXTRA_TRAILER_USD} Dólares Americanos** (Convertidos a cotización BROU: ${COTIZACION_BROU_MAX})")

    # 4. Cálculo de Distancia (Ida y Vuelta + 20% curvas)
    p_orig = df_localidades[(df_localidades['departamento']==d_o) & (df_localidades['localidad']==l_o)].iloc[0]
    p_dest = df_localidades[(df_localidades['departamento']==d_d) & (df_localidades['localidad']==l_d)].iloc[0]
    dist_total = (math.sqrt((p_dest['cx'] - p_orig['cx'])**2 + (p_dest['cy'] - p_orig['cy'])**2) / 1000) * 1.2 * 2
    
    # 5. Cálculo Final Actualizado
    tarifa = TARIFA_MUDANZA_KM if "📦" in rubro else TARIFA_BARCO_KM
    costo_flete_base = dist_total * tarifa
    
    # IMPORTANTE: Aquí se suma el extra de los 200 dólares en pesos al total
    total_pesos = costo_flete_base + extra_pesos_brou
    total_dolares = total_pesos / COTIZACION_BROU_MAX

    # --- RESULTADO FINAL ---
    st.markdown("---")
    st.markdown(f"""
        <div class="price-box">
            <h3 style="margin:0; color:#2e7d32;">PRESUPUESTO ESTIMADO (IDA Y VUELTA)</h3>
            <h1 style="margin:0; font-size: 45px; color:#1b5e20;">$ {total_pesos:,.2f} UYU</h1>
            <p style="font-size: 24px; color:#01579b;"><b>U$S {total_dolares:,.2f} Dólares Americanos</b></p>
            <hr>
            <p style="font-size: 14px; color:#555; text-align: left;">
                • Recorrido Total: {round(dist_total,1)} km<br>
                • Flete base: ${costo_flete_base:,.2f} UYU<br>
                • Extra Pesada: {"U$S 200.00" if es_pesada else "No aplica"}<br>
                • Cotización aplicada: ${COTIZACION_BROU_MAX} (BROU Máxima)
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📷 Registro de Carga")
    foto = st.file_uploader("Suba una imagen del objeto (OBLIGATORIO)", type=['png', 'jpg', 'jpeg'])

    if st.button("📧 SOLICITAR COTIZACIÓN"):
        if foto is not None:
            asunto = urllib.parse.quote(f"Nueva Cotización CLS - {l_o} a {l_d}")
            mensaje = urllib.parse.quote(f"Origen: {l_o}, {d_o}\nDestino: {l_d}, {d_d}\nDistancia Total: {round(dist_total,1)} km\nTotal: $ {round(total_pesos,2)} UYU (U$S {round(total_dolares,2)} USD)")
            email_url = f"mailto:conexionlogisticasur@gmail.com?subject={asunto}&body={mensaje}"
            st.balloons()
            st.markdown(f'<a href="{email_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#01579b; color:white; padding:15px; border-radius:8px; text-align:center; font-weight:bold;">HACÉ CLIC AQUÍ PARA ENVIAR EL EMAIL</div></a>', unsafe_allow_html=True)
        else:
            st.error("⚠️ Debe subir una foto para procesar la cotización.")
else:
    st.error("⚠️ No se encontró el archivo de localidades.")

st.sidebar.markdown(f"**Desarrollador:** Leonardo Olivera")
