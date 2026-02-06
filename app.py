import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from fpdf import FPDF
import tempfile
import os

# --- LÓGICA DE DIBUJO (Mantenemos la anterior para consistencia) ---
def dibujar_plano_detallado(mueble):
    ESC = 10 
    img_w = int(mueble['ancho'] * ESC) + 200
    img_h = 600
    img = Image.new('RGB', (img_w, img_h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    x_start, y_piso = 100, 500
    h_px = int(mueble['alto'] * ESC)
    y_top = y_piso - h_px
    
    draw.rectangle([x_start, y_top, x_start + mueble['ancho']*ESC, y_piso], outline="black", width=3)
    
    x_actual = x_start
    for sec in mueble['secciones']:
        w_sec_px = int(sec['ancho'] * ESC)
        draw.rectangle([x_actual, y_top, x_actual + w_sec_px, y_piso], outline="black", width=2)
        
        # Cotas rojas de cada sección
        draw.line([x_actual + 2, y_piso + 20, x_actual + w_sec_px - 2, y_piso + 20], fill="red", width=1)
        draw.text((x_actual + w_sec_px/2 - 5, y_piso + 25), f"{sec['ancho']}", fill="red")
        draw.text((x_actual + 5, y_top + 5), sec['tipo'], fill="black")
        x_actual += w_sec_px
        
    return img

# --- FUNCIÓN PARA CREAR EL PDF ---
def crear_pdf(mueble, imagen_plano):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado Profesional
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Cotización y Plano: {mueble['nombre']}", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Medidas Generales: {mueble['ancho']}\" Ancho x {mueble['alto']}\" Alto", ln=True)
    
    # Guardar imagen temporalmente para el PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        imagen_plano.save(tmpfile.name)
        # Insertar imagen en el PDF (ajustando al ancho de la página)
        pdf.image(tmpfile.name, x=10, y=40, w=190)
        tmp_path = tmpfile.name

    # Tabla de especificaciones
    pdf.ln(80) # Espacio después de la imagen
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Detalle de Secciones Internas:", ln=True)
    pdf.set_font("Arial", size=10)
    
    for i, sec in enumerate(mueble['secciones']):
        pdf.cell(200, 8, txt=f"- Sección {i+1}: {sec['tipo']} de {sec['ancho']} pulgadas.", ln=True)

    pdf_output = pdf.output(dest='S').encode('latin-1')
    os.unlink(tmp_path) # Borrar archivo temporal
    return pdf_output

# --- INTERFAZ DE USUARIO ---
if st.session_state.proyecto:
    for i, m in enumerate(st.session_state.proyecto):
        st.subheader(f"📋 Vista Previa: {m['nombre']}")
        img_final = dibujar_plano_detallado(m)
        st.image(img_final, use_container_width=True)
        
        # Botón de Descarga PDF
        pdf_data = crear_pdf(m, img_final)
        st.download_button(
            label="📥 Descargar Plano en PDF",
            data=pdf_data,
            file_name=f"Plano_{m['nombre']}.pdf",
            mime="application/pdf"
        )
        
