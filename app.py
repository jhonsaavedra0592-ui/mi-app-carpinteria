import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
import tempfile

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Carpintería Pro: Master Design", layout="wide")

if "proyecto" not in st.session_state:
    st.session_state.proyecto = []

st.title("🚀 Sistema Integral de Diseño, Despiece y Nesting")

# --- 2. HERRAMIENTAS DE DISEÑO (BARRA LATERAL) ---
with st.sidebar:
    st.header("Configurador de Mueble")
    
    muro = st.selectbox("Asignar a Pared/Muro", ["Pared A (Principal)", "Pared B (Lateral)", "Isla"])
    tipo = st.selectbox("Tipo de Mueble", ["Gabinete Bajo", "Alacena Superior", "Torre Despensa", "Cajonera"])
    
    ancho = st.number_input("Ancho (in)", 5.0, 120.0, 30.0)
    alto = st.number_input("Alto (in)", 10.0, 120.0, 34.5)
    prof = st.number_input("Profundidad (in)", 10.0, 30.0, 24.0)
    
    # IMPORTANTE: Estos campos definen el diseño interno
    div = st.slider("Número de divisiones/cajones", 1, 6, 3)
    espesor = st.selectbox("Espesor del material (in)", [0.5, 0.625, 0.75], index=2)

    if st.button("➕ Agregar al Proyecto"):
        st.session_state.proyecto.append({
            "muro": muro,
            "tipo": tipo,
            "ancho": ancho,
            "alto": alto,
            "prof": prof,
            "div": div,
            "espesor": espesor
        })
        st.success(f"{tipo} agregado!")

    if st.button("🗑️ Reiniciar Todo"):
        st.session_state.proyecto = []
        st.rerun()

# --- 3. LÓGICA DE DIBUJO TÉCNICO ---
def dibujar_muebles(modulos_muro):
    # Escala: 1 pulgada = 8 píxeles
    ancho_px = int(sum(m['ancho'] for m in modulos_muro) * 8) + 100
    alto_canvas = 500
    img = Image.new('RGB', (ancho_px, alto_canvas), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    x_cursor = 50
    y_suelo = 400
    
    for m in modulos_muro:
        w = int(m['ancho'] * 8)
        h = int(m['alto'] * 8)
        y_top = y_suelo - h
        
        # 1. Dibujar el marco exterior
        draw.rectangle([x_cursor, y_top, x_cursor + w, y_suelo], outline="black", width=3, fill="#F1F1F1")
        
        # 2. DIBUJAR DIVISIONES (Esto es lo que faltaba)
        if m['div'] > 1:
            alto_seccion = h / m['div']
            for i in range(1, m['div']):
                y_div = y_top + (i * alto_seccion)
                # Línea de división
                draw.line([(x_cursor, y_div), (x_cursor + w, y_div)], fill="black", width=2)
                
                # Jaladeras (manijas) para que parezca mueble real
                centro_x = x_cursor + (w / 2)
                y_jaladera = y_div - (alto_seccion / 2)
                draw.line([centro_x - 15, y_jaladera, centro_x + 15, y_jaladera], fill="gray", width=4)
            
            # Jaladera del último cajón/espacio
            y_jaladera_final = y_suelo - (alto_seccion / 2)
            draw.line([x_cursor + (w/2) - 15, y_jaladera_final, x_cursor + (w/2) + 15, y_jaladera_final], fill="gray", width=4)

        # Etiquetas de medidas
        draw.text((x_cursor + 5, y_top - 20), f"{m['ancho']}\" x {m['alto']}\"", fill="blue")
        x_cursor += w + 10
        
    return img

# --- 4. VISUALIZACIÓN EN TABS ---
if st.session_state.proyecto:
    tab_planos, tab_despiece, tab_nesting = st.tabs(["🖼️ Planos", "📋 Despiece", "📐 Nesting"])
    
    with tab_planos:
        muros = sorted(list(set(m['muro'] for m in st.session_state.proyecto)))
        for m_nombre in muros:
            st.subheader(f"📍 {m_nombre}")
            modulos_muro = [m for m in st.session_state.proyecto if m['muro'] == m_nombre]
            img_plano = dibujar_muebles(modulos_muro)
            st.image(img_plano, use_container_width=True)

    with tab_despiece:
        st.subheader("Guía de Corte")
        # Aquí puedes reutilizar tu función de despiece anterior
        for i, mod in enumerate(st.session_state.proyecto):
            st.write(f"**Módulo {i+1}: {mod['tipo']}**")
            st.write(f"Medidas externas: {mod['ancho']}x{mod['alto']}x{mod['prof']}")
            # (Lógica de despiece simplificada para el ejemplo)
            st.caption("Corte laterales: 2 piezas de " + str(mod['alto']) + "x" + str(mod['prof']))

else:
    st.info("👈 Comienza agregando muebles en la barra lateral para generar el diseño.")
    
