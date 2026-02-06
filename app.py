import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from fpdf import FPDF
import tempfile

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Diseñador de Gabinetes", layout="wide")

if "modulos" not in st.session_state:
    st.session_state.modulos = []

st.title("🪚 Diseñador de Gabinetes y Cajoneras")

# --- 2. ENTRADA DE DATOS ---
with st.sidebar:
    st.header("Dimensiones Generales")
    nombre = st.text_input("Nombre del Mueble", "Gabinete Base")
    ancho = st.number_input("Ancho total (pulg)", 1.0, 100.0, 30.0)
    alto = st.number_input("Alto total (pulg)", 1.0, 100.0, 36.0)
    
    st.divider()
    st.subheader("Configuración Interna")
    # Nueva función: Número de espacios/cajones
    num_divisiones = st.number_input("Número de espacios/cajones", 1, 10, 3)
    tipo_division = st.selectbox("Tipo de frente", ["Cajones", "Repisas Abiertas", "Puertas"])
    
    st.divider()
    st.subheader("Costos")
    costo_hoja = st.number_input("Precio Hoja", value=850.0)
    mano_obra_pulg = st.number_input("Mano de obra x pulgada", value=15.0)
    
    btn_add = st.button("➕ Agregar al Proyecto")
    
    if st.button("🗑️ Limpiar Todo"):
        st.session_state.modulos = []
        st.rerun()

# --- 3. LÓGICA DE CÁLCULO ---
if btn_add:
    # Cálculo simple de costo (área + estructura interna extra)
    area_frontal = ancho * alto
    costo_base = (area_frontal / (48*96)) * costo_hoja
    # Sumamos un extra por cada división (material de fondo de cajón o repisa)
    costo_interno = (num_divisiones * (ancho * 20) / (48*96)) * costo_hoja 
    total = costo_base + costo_interno + (ancho * mano_obra_pulg)
    
    st.session_state.modulos.append({
        "Nombre": nombre,
        "Ancho": ancho,
        "Alto": alto,
        "Divisiones": num_divisiones,
        "Tipo": tipo_division,
        "Costo": round(total, 2)
    })

# --- 4. VISUALIZACIÓN DETALLADA ---
if st.session_state.modulos:
    col_t, col_v = st.columns([1, 1])
    
    with col_t:
        st.subheader("📋 Resumen")
        st.table(pd.DataFrame(st.session_state.modulos)[["Nombre", "Divisiones", "Tipo", "Costo"]])
        st.metric("Total", f"${sum(m['Costo'] for m in st.session_state.modulos):,.2f}")

    with col_v:
        st.subheader("📐 Vista Esquemática")
        # Lienzo para el dibujo
        img = Image.new('RGB', (800, 450), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        x_inicio = 50
        for m in st.session_state.modulos:
            w, h = int(m["Ancho"] * 5), int(m["Alto"] * 5)
            y_piso = 400
            y_techo = y_piso - h
            
            # 1. Dibujar el marco exterior del gabinete
            draw.rectangle([x_inicio, y_techo, x_inicio + w, y_piso], outline="black", width=4, fill="#D2B48C")
            
            # 2. Dibujar las divisiones (cajones o repisas)
            alto_espacio = h / m["Divisiones"]
            for i in range(m["Divisiones"]):
                y_div = y_techo + (i * alto_espacio)
                # Dibujar cada línea de división
                draw.rectangle([x_inicio, y_div, x_inicio + w, y_div + alto_espacio], outline="#5D4037", width=2)
                
                # Si son cajones, dibujar un pequeño "tirador" o manija
                if m["Tipo"] == "Cajones":
                    cx, cy = x_inicio + (w/2), y_div + (alto_espacio/2)
                    draw.ellipse([cx-5, cy-2, cx+5, cy+2], fill="black")
            
            draw.text((x_inicio, y_piso + 10), m["Nombre"], fill="black")
            x_inicio += w + 40
            
        st.image(img, use_container_width=True)
        
