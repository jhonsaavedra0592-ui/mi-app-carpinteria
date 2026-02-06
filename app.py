import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import tempfile

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Carpintería Pro - Planos Detallados", layout="wide")

if "proyecto" not in st.session_state:
    st.session_state.proyecto = []

st.title("📐 Generador de Planos Técnicos de Muebles")

# --- BARRA LATERAL: CONFIGURACIÓN DE MÓDULOS ---
with st.sidebar:
    st.header("Agregar Componente")
    
    # Selección de tipo de espacio específico
    tipo = st.selectbox("Tipo de Espacio", [
        "Gabinete de Basura (Trash)", 
        "Módulo de Cajones", 
        "Base de Fregadero (Sink)", 
        "Espacio Lavavajillas (DW)",
        "Gabinete de Puerta Estándar"
    ])
    
    ancho = st.number_input("Ancho del módulo (pulg)", 5.0, 100.0, 24.0)
    alto = st.number_input("Alto del módulo (pulg)", 10.0, 100.0, 36.0)
    
    if tipo == "Módulo de Cajones":
        detalles = st.slider("Número de cajones", 1, 5, 3)
    else:
        detalles = 0 # Para puertas o espacios abiertos

    if st.button("➕ Añadir al Plano"):
        st.session_state.proyecto.append({
            "tipo": tipo,
            "ancho": ancho,
            "alto": alto,
            "detalles": detalles
        })

    st.divider()
    if st.button("🗑️ Borrar Todo"):
        st.session_state.proyecto = []
        st.rerun()

# --- DIBUJO DEL PLANO TÉCNICO ---
def dibujar_plano(modulos):
    # Calcular dimensiones totales
    ancho_total_pulg = sum(m['ancho'] for m in modulos)
    alto_max_pulg = max(m['alto'] for m in modulos) if modulos else 40
    
    # Escala: 1 pulgada = 10 píxeles para mayor nitidez
    margen = 80
    canvas_w = int(ancho_total_pulg * 10) + (margen * 2)
    canvas_h = int(alto_max_pulg * 10) + (margen * 3)
    
    img = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    x_cursor = margen
    y_suelo = canvas_h - margen
    
    for m in modulos:
        w = int(m['ancho'] * 10)
        h = int(m['alto'] * 10)
        y_techo = y_suelo - h
        
        # 1. Dibujar estructura externa (líneas negras finas como plano)
        draw.rectangle([x_cursor, y_techo, x_cursor + w, y_suelo], outline="black", width=2)
        
        # 2. Detalles según tipo
        if m['tipo'] == "Módulo de Cajones":
            h_cajon = h / m['detalles']
            for i in range(m['detalles']):
                y_c = y_techo + (i * h_cajon)
                draw.rectangle([x_cursor + 5, y_c + 5, x_cursor + w - 5, y_c + h_cajon - 5], outline="black", width=1)
                # Jaladera
                draw.line([x_cursor + w/2 - 15, y_c + h_cajon/2, x_cursor + w/2 + 15, y_c + h_cajon/2], fill="black", width=2)
        
        elif m['tipo'] == "Base de Fregadero (Sink)":
            # Dibujar dos puertas
            draw.line([x_cursor + w/2, y_techo + 10, x_cursor + w/2, y_suelo - 10], fill="black", width=1)
            # Jaladeras circulares
            draw.ellipse([x_cursor + w/2 - 15, y_techo + 40, x_cursor + w/2 - 5, y_techo + 50], outline="black")
            draw.ellipse([x_cursor + w/2 + 5, y_techo + 40, x_cursor + w/2 + 15, y_techo + 50], outline="black")
            
        elif m['tipo'] == "Gabinete de Basura (Trash)":
            draw.rectangle([x_cursor + 10, y_techo + 10, x_cursor + w - 10, y_suelo - 10], outline="black", width=1)
            draw.line([x_cursor + 20, y_techo + 30, x_cursor + w - 20, y_techo + 30], fill="black", width=3)

        # 3. Cotas (Medidas en el dibujo)
        draw.text((x_cursor + w/2 - 10, y_suelo + 5), f"{m['ancho']}\"", fill="red")
        
        x_cursor += w

    # Cota total
    if modulos:
        draw.line([margen, y_suelo + 40, x_cursor, y_suelo + 40], fill="red", width=2)
        draw.text((canvas_w/2 - 20, y_suelo + 45), f"Total: {ancho_total_pulg}\" inches", fill="red")

    return img

# --- VISUALIZACIÓN ---
if st.session_state.proyecto:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Lista de Componentes")
        df = pd.DataFrame(st.session_state.proyecto)
        st.table(df[["tipo", "ancho", "alto"]])
        
    with col2:
        st.subheader("Plano de Alzado (Frontal)")
        imagen_plano = dibujar_plano(st.session_state.proyecto)
        st.image(imagen_plano, use_container_width=True, caption="Medidas en pulgadas")
else:
    st.info("Agrega módulos para empezar a armar tu plano técnico.")
