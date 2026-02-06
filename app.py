import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from fpdf import FPDF
import tempfile
import os

# --- 1. INICIALIZACIÓN (ESTO CORRIGE TU ERROR) ---
st.set_page_config(page_title="Carpintería Pro: Cotizador IA", layout="wide")

# Inicializamos todas las variables necesarias en el session_state
if "proyecto" not in st.session_state:
    st.session_state.proyecto = []
if "ideas_ia" not in st.session_state:
    st.session_state.ideas_ia = []
if "secciones_temp" not in st.session_state:
    st.session_state.secciones_temp = []

st.title("🚀 Sistema de Diseño, PDF y Cotización")

# --- 2. CONFIGURACIÓN DE COSTOS (NUEVO) ---
with st.sidebar:
    st.header("💰 Configuración de Precios")
    precio_pulgada = st.number_input("Precio por pulgada lineal ($)", value=15.0)
    costo_fijo_herrajes = st.number_input("Costo base herrajes/instalación ($)", value=100.0)

    st.divider()
    st.header("📏 Medidas del Mueble")
    ancho_total = st.number_input("Ancho Total (in)", 5.0, 200.0, 60.0)
    alto_mueble = st.number_input("Alto (in)", 10.0, 100.0, 36.0)
    
    # ... (Aquí iría tu lógica anterior de agregar secciones_temp) ...

# --- 3. FUNCIÓN DE PDF CON COSTOS ---
def crear_pdf_profesional(mueble, imagen_plano, costo_total):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(200, 15, txt="COTIZACIÓN FORMAL DE CARPINTERÍA", ln=True, align='C')
    
    # Plano
    pdf.ln(5)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        imagen_plano.save(tmp.name)
        pdf.image(tmp.name, x=10, y=35, w=190)
        tmp_path = tmp.name

    # Detalles de costo
    pdf.set_y(150) # Moverse abajo del dibujo
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(200, 10, txt=f"PRECIO TOTAL ESTIMADO: ${costo_total:,.2f}", ln=True, align='R')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Especificaciones Técnicas:", ln=True)
    
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 8, txt=f"- Dimensiones: {mueble['ancho']}\" x {mueble['alto']}\"", ln=True)
    for sec in mueble['secciones']:
        pdf.cell(200, 7, txt=f"  > {sec['tipo']}: {sec['ancho']} pulgadas.", ln=True)

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    os.unlink(tmp_path)
    return pdf_bytes

# --- 4. MOSTRAR RESULTADOS Y COTIZACIÓN ---
if st.session_state.proyecto:
    for m in st.session_state.proyecto:
        # Calcular costo basado en el ancho
        costo_mueble = (m['ancho'] * precio_pulgada) + costo_fijo_herrajes
        
        st.subheader(f"📋 Mueble: {m['nombre']}")
        col_img, col_info = st.columns([2, 1])
        
        with col_img:
            # Usamos la función de dibujo que ya tenías
            img_plano = dibujar_plano_detallado(m) 
            st.image(img_plano, use_container_width=True)
            
        with col_info:
            st.metric("Presupuesto Estimado", f"${costo_mueble:,.2f}")
            
            pdf_data = crear_pdf_profesional(m, img_plano, costo_mueble)
            st.download_button(
                label="📄 Descargar Cotización PDF",
                data=pdf_data,
                file_name=f"Cotizacion_{m['nombre']}.pdf",
                mime="application/pdf"
            )
else:
    st.info("👈 Comienza agregando un mueble para ver el plano y la cotización.")
    
