import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Carpintería Pro: Master Design", layout="wide")

if "proyecto" not in st.session_state:
    st.session_state.proyecto = []

st.title("🚀 Sistema Integral: Diseño y Planos")

# --- 2. BARRA LATERAL ---
with st.sidebar:
    st.header("Configurador de Mueble")
    muro = st.selectbox("Pared", ["Pared A", "Pared B", "Isla"])
    tipo = st.selectbox("Tipo", ["Gabinete Bajo", "Alacena", "Cajonera"])
    
    ancho = st.number_input("Ancho (in)", 5.0, 120.0, 30.0)
    alto = st.number_input("Alto (in)", 10.0, 120.0, 34.5)
    
    # Asegúrate de mover este slider antes de dar click a Agregar
    num_div = st.slider("Número de divisiones/cajones", 1, 10, 3)
    
    if st.button("➕ Agregar al Proyecto"):
        st.session_state.proyecto.append({
            "muro": muro,
            "tipo": tipo,
            "ancho": ancho,
            "alto": alto,
            "div": int(num_div)  # Guardamos como entero
        })
        st.success("¡Agregado!")

    if st.button("🗑️ Limpiar Todo"):
        st.session_state.proyecto = []
        st.rerun()

# --- 3. FUNCIÓN DE DIBUJO CORREGIDA ---
def generar_plano_tecnico(modulos):
    # Definir dimensiones del lienzo (canvas)
    ancho_canvas = int(sum(m['ancho'] for m in modulos) * 10) + 150
    alto_canvas = 600
    img = Image.new('RGB', (ancho_canvas, alto_canvas), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    x_offset = 50
    piso = 500
    
    for m in modulos:
        # Convertir pulgadas a píxeles (Escala 1:10)
        w = int(m['ancho'] * 10)
        h = int(m['alto'] * 10)
        techo = piso - h
        
        # 1. Dibujar el RECUADRO PRINCIPAL
        draw.rectangle([x_offset, techo, x_offset + w, piso], outline="black", width=4)
        
        # 2. DIBUJAR DIVISIONES (Lógica forzada)
        n_espacios = m['div']
        if n_espacios > 1:
            alto_cada_espacio = h / n_espacios
            for i in range(1, n_espacios):
                # Calcular altura de la línea divisoria
                y_linea = techo + (i * alto_cada_espacio)
                
                # Dibujar línea horizontal de lado a lado del mueble
                draw.line([(x_offset, y_linea), (x_offset + w, y_linea)], fill="black", width=2)
                
                # Dibujar una pequeña "manija" o jaladera en el centro de cada espacio
                cx = x_offset + (w / 2)
                cy = y_linea - (alto_cada_espacio / 2)
                draw.line([cx - 15, cy, cx + 15, cy], fill="gray", width=4)
            
            # Dibujar la jaladera del último espacio (el de abajo)
            cy_final = piso - (alto_cada_espacio / 2)
            draw.line([x_offset + (w/2) - 15, cy_final, x_offset + (w/2) + 15, cy_final], fill="gray", width=4)

        # Cotas de texto
        draw.text((x_offset, techo - 20), f"{m['ancho']}\" x {m['alto']}\" ({m['div']} div)", fill="blue")
        
        x_offset += w + 20 # Espacio entre muebles
        
    return img

# --- 4. MOSTRAR RESULTADOS ---
if st.session_state.proyecto:
    tab1, tab2 = st.tabs(["🖼️ Ver Planos", "📋 Lista de Datos"])
    
    with tab1:
        muros = set(m['muro'] for m in st.session_state.proyecto)
        for m_nombre in muros:
            st.subheader(f"📍 {m_nombre}")
            lista_muro = [m for m in st.session_state.proyecto if m['muro'] == m_nombre]
            plano_final = generar_plano_tecnico(lista_muro)
            st.image(plano_final, use_container_width=True)
            
    with tab2:
        st.write(st.session_state.proyecto)
else:
    st.info("Usa el configurador de la izquierda para diseñar tu primer mueble.")
    
