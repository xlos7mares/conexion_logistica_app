import streamlit as st
import pandas as pd
import re
import math
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CLS - Cotizador Oficial", page_icon="🚛", layout="centered")

# --- VALORES DEL DÍA (Ajustables manualmente) ---
TARIFA_MUDANZA_KM = 55.0  
TARIFA_BARCO_KM = 80.0    
EXTRA_TRAILER_USD = 200.0   # Los 200 Dólares Americanos solicitados
COTIZACION_BROU_MAX = 42.80  # Cotización Venta del día (ajustar según el BROU)

# --- DISEÑO RESPONSIVO (LOGO ADAPTABLE A CELULAR) ---
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
        <p style="color: gray; font-size: 16px; margin-top: 5px;">Transporte Nacional e Internacional</p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# --- CARGA DE DATOS (CSV LOCALIDADES) ---
@st.cache_data
def cargar_datos():
    try:
        # Cargamos el archivo que subiste
        df = pd.read_csv('localidades-29-7nm (1).csv')
        def get_centroid(wkt):
            # Extrae coordenadas X e Y del formato MULTIPOLYGON
            c = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", wkt)]
            if c:
                return (sum(c[0::2])/len(c[0::2]), sum(c[1::2])/len(c[1::2]))
            return (0,0)
        df['cx'], df['cy'] = zip(*df['wkt'].apply(get_centroid))
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV: {e}")
        return None

df_localidades = cargar_datos()

if df_localidades is not None:
    # 1. Selección de Rubro
    rubro = st.radio("### 🛠️ ¿Qué desea cotizar?", ["📦 Mudanzas, Mercaderías u Objetos", "🚤 Embarcaciones (Lanchas/Cruceros)"], horizontal=True)

    # 2. Origen y Destino
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📍 ORIGEN**")
        d_o = st.selectbox("Dpto. Origen:", sorted(df_localidades['departamento'].unique()), key="do")
        l_o = st.selectbox("Ciudad Origen:", sorted(df_localidades[df_localidades['departamento'] == d_o]['localidad'].unique()), key="lo")
    with col2:
        st.markdown("**🏁 DESTINO**")
        d_d = st.selectbox("Dpto. Destino:", sorted(df_localidades['departamento'].unique()), key="dd")
        l_d = st.selectbox("Ciudad Destino:", sorted(df_localidades[df_localidades['departamento'] == d_d]['localidad'].unique()), key="ld")

    # 3. Lógica de Carga Pesada y Trailer (Suma U$S 200)
    extra_pesos_brou = 0.0
    es_pesada = False
    
    if "🚤" in rubro:
        tipo_b = st.selectbox("Detalle de la Embarcación:", 
                              ["Lancha chica (Estándar)", "Crucero mediano", "Embarcación Grande (Carga Pesada + Tráiler)"])
        
        if "Carga Pesada" in tipo_b:
            es_pesada = True
            # Convertimos los U$S 200 a Pesos Uruguayos usando la cotización BROU del día
            extra_pesos_brou = EXTRA_TRAILER_USD * COTIZACION_BROU_MAX
            st.warning(f"🔔 Se aplicó el costo adicional por Tráiler Pesado: **U$S {EXTRA_TRAILER_USD} Dólares Americanos**")

    # 4. Cálculo de Distancia (Ida y Vuelta + 20% margen curvas)
    p_orig = df_localidades[(df_localidades['departamento']==d_o) & (df_localidades['localidad']==l_o)].iloc[0]
    p_dest = df_localidades[(df_localidades['departamento']==d_d) & (df_localidades['localidad']==l_d)].iloc[0]
    
    # Distancia lineal -> km -> margen -> ida y vuelta
    dist_total = (math.sqrt((p_dest['cx'] - p_orig['cx'])**2 + (p_dest['cy'] - p_orig['cy'])**2) / 1000) * 1.2 * 2
    
    # 5. Cálculo del Precio Final
    tarifa_aplicada = TARIFA_MUDANZA_KM if "📦" in rubro else TARIFA_BARCO_KM
    costo_flete_base = dist_total * tarifa_aplicada
    
    # RESULTADO EN PESOS: (Km totales * Tarifa) + (U$S 200 * Cotización BROU)
    total_pesos_final = costo_flete_base + extra_pesos_brou
    total_dolares_final = total_pesos_final / COTIZACION_BROU_MAX

    # --- MOSTRAR RESULTADO ---
    st.markdown("---")
    st.markdown(f"""
        <div class="price-box">
            <h3 style="margin:0; color:#2e7d32;">PRESUPUESTO ESTIMADO (CON RETORNO)</h3>
            <h1 style="margin:0; font-size: 48px; color:#1b5e20;">$ {total_pesos_final:,.2f} UYU</h1>
            <p style="font-size: 24px; color:#01579b;"><b>U$S {total_dolares_final:,.2f} Dólares Americanos</b></p>
            <hr style="border: 0.5px solid #ccc;">
            <p style="font-size: 14px; color:#555; text-align: left;">
                • Recorrido Total: {round(dist_total,1)} km (Ida y Vuelta)<br>
                • Tarifa por km: ${tarifa_aplicada} UYU<br>
                • Extra Tráiler: {"U$S 200.00" if es_pesada else "No aplica"}<br>
                • Cotización BROU aplicada: ${COTIZACION_BROU_MAX}
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    # --- SUBIDA DE IMAGEN ---
    st.subheader("📷 Registro de Carga")
    foto = st.file_uploader("Suba una imagen de lo que desea trasladar (OBLIGATORIO)", type=['png', 'jpg', 'jpeg'])

    # --- BOTÓN DE ENVÍO POR EMAIL ---
    if st.button("📧 SOLICITAR COTIZACIÓN"):
        if foto is not None:
            # Preparar link de email
            asunto = urllib.parse.quote(f"Nueva Cotización - {l_o} a {l_d}")
            mensaje = urllib.parse.quote(
                f"Solicitud de Traslado\n"
                f"Rubro: {rubro}\n"
                f"Origen: {l_o}, {d_o}\n"
                f"Destino: {l_d}, {d_d}\n"
                f"Distancia Total: {round(dist_total,1)} km\n"
                f"Total Estimado: $ {round(total_pesos_final,2)} UYU (U$S {round(total_dolares_final,2)} USD)"
            )
            email_url = f"mailto:conexionlogisticasur@gmail.com?subject={asunto}&body={mensaje}"
            
            st.balloons()
            st.markdown(f'''
                <a href="{email_url}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#01579b; color:white; padding:18px; border-radius:8px; text-align:center; font-weight:bold; font-size:18px;">
                        HAGA CLIC AQUÍ PARA ENVIAR EL EMAIL FINAL
                    </div>
                </a>
            ''', unsafe_allow_html=True)
        else:
            st.error("⚠️ Debe subir una foto de la carga para que podamos procesar la solicitud.")
else:
    st.error("⚠️ No se pudo encontrar el archivo 'localidades-29-7nm (1).csv'. Verifique que esté en su repositorio de GitHub.")

st.sidebar.markdown(f"**Desarrollador:** Leonardo Olivera")
st.sidebar.caption("Software & IA | Estudiante de Agronomía")
