import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from fpdf import FPDF
import tempfile
import os

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Carpintería Pro: Sistema Integral", layout="wide")

# Evita errores de variables no definidas al cargar la app
if "proyecto" not in st.session_state:
    st.session_state.proyecto = []
if "secciones_temp" not in st.session_state:
    st.session_state.secciones_temp = []

# --- 2. MOTOR DE DIBUJO TÉCNICO (UNIVERSAL) ---
def dibujar_plano_profesional(mueble):
    ESC = 12  # Escala: 1 pulgada = 12 píxeles
    ancho_px = int(mueble['ancho'] * ESC) + 200
    alto_px = 700
    img = Image.new('RGB', (ancho_px, alto_px), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    x_offset = 100
    piso_y = 550
    h_px = int(mueble['alto'] * ESC)
    y_top = piso_y - h_px
    
    # Marco exterior total
    draw.rectangle([x_offset, y_top, x_offset + mueble['ancho']*ESC, piso_y], outline="black", width=4)
    
    x_cursor = x_offset
    for sec in mueble['secciones']:
        w_sec_px = int(sec['ancho'] * ESC)
        
        # Dibujar cada sección/módulo
        draw.rectangle([x_cursor, y_top, x_cursor + w_sec_px, piso_y], outline="black", width=2)
        
        # Divisiones internas (Cajones o Repisas)
        if sec['div'] > 1:
            alto_div = h_px / sec['div']
            for i in range(1, int(sec['div'])):
                y_div = y_top + (i * alto_div)
                draw.line([(x_cursor, y_div), (x_cursor + w_sec_px, y_div)], fill="black", width=1)
                # Jaladera (Handle)
                draw.line([x_cursor + w_sec_px/2 - 15, y_div - 8, x_cursor + w_sec_px/2 + 15, y_div - 8], fill="gray", width=3)
        
        # COTAS ROJAS (Medidas individuales)
        draw.line([x_cursor + 5, piso_y + 25, x_cursor + w_sec_px - 5, piso_y + 25], fill="red", width=1)
        draw.text((x_cursor + w_sec_px/2 - 10, piso_y + 30), f"{sec['ancho']}\"", fill="red")
        
        # Etiqueta de tipo
        draw.text((x_cursor + 10, y_top + 10), sec['tipo'], fill="black")
        x_cursor += w_sec_px

    # Cota de Altura (Lateral)
    draw.line([x_offset - 30, y_top, x_offset - 30, piso_y], fill="blue", width=1)
    draw.text((x_offset - 70, y_top + h_px/2), f"{mueble['alto']}\"", fill="blue")
    
    # Cota Total (Inferior)
    draw.line([x_offset, piso_y + 70, x_offset + mueble['ancho']*ESC, piso_y + 70], fill="red", width=2)
    draw.text((x_offset + (mueble['ancho']*ESC)/2 - 20, piso_y + 80), f"TOTAL: {mueble['ancho']} in", fill="red")
    
    return img

# --- 3. FUNCIÓN DE EXPORTACIÓN PDF ---
def generar_pdf_cotizacion(mueble, imagen, costo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"COTIZACIÓN TÉCNICA: {mueble['nombre']}", ln=True, align='C')
    
    # Insertar Imagen del Plano
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        imagen.save(tmp.name)
        pdf.image(tmp.name, x=10, y=30, w=190)
        tmp_path = tmp.name
    
    pdf.set_y(140)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(200, 10, txt=f"PRECIO ESTIMADO: ${costo:,.2f} USD", ln=True, align='R')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Desglose de diseño:", ln=True)
    for s in mueble['secciones']:
        pdf.cell(200, 8, txt=f"- {s['tipo']} de {s['ancho']}\" con {s['div']} división(es).", ln=True)
    
    pdf_output = pdf.output(dest='S').encode('latin-1')
    os.unlink(tmp_path)
    return pdf_output

# --- 4. INTERFAZ DE USUARIO (SIDEBAR) ---
with st.sidebar:
    st.header("🛠️ Configuración General")
    nombre_p = st.text_input("Nombre del Proyecto", "Cocina Moderna")
    ancho_t = st.number_input("Ancho Total del Espacio (in)", 10.0, 300.0, 96.0)
    alto_t = st.number_input("Alto del Gabinete (in)", 10.0, 120.0, 34.5)
    costo_pulgada = st.number_input("Precio por pulgada lineal ($)", 5.0, 100.0, 15.0)

    st.divider()
    st.subheader("🧩 Añadir Secciones (Medidas Reales)")
    ancho_s = st.number_input("Ancho Sección", 5.0, 100.0, 20.0)
    tipo_s = st.selectbox("Función", ["Cajonera", "Fregadero", "Puertas", "Basura", "DW", "Torre"])
    div_s = st.number_input("Nº de divisiones", 1, 10, 3)
    
    if st.button("➕ Agregar Sección"):
        actual = sum(s['ancho'] for s in st.session_state.secciones_temp)
        if actual + ancho_s <= ancho_t:
            st.session_state.secciones_temp.append({"ancho": ancho_s, "tipo": tipo_s, "div": div_s})
            st.success(f"Sección de {ancho_s}\" añadida")
        else:
            st.error("Sobrepasa el ancho total")

    if st.button("💾 Guardar Mueble"):
        st.session_state.proyecto.append({
            "nombre": nombre_p, "ancho": ancho_t, "alto": alto_t,
            "secciones": st.session_state.secciones_temp
        })
        st.session_state.secciones_temp = []
        st.rerun()

    if st.button("🗑️ Limpiar Todo"):
        st.session_state.proyecto = []
        st.rerun()

# --- 5. CUERPO PRINCIPAL ---
st.header("📋 Vista de Diseño y Planos")

if st.session_state.proyecto:
    for m in st.session_state.proyecto:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            # Cálculo de Costo
            total_costo = (m['ancho'] * costo_pulgada) + 150 # 150 de base fija
            
            with col1:
                img_final = dibujar_plano_profesional(m)
                st.image(img_final, use_container_width=True)
            
            with col2:
                st.write(f"### {m['nombre']}")
                st.metric("Presupuesto", f"${total_costo:,.2f}")
                
                pdf_bytes = generar_pdf_cotizacion(m, img_final, total_costo)
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"Plano_{m['nombre']}.pdf",
                    mime="application/pdf"
                )
                
                # Sugerencia de IA según el espacio
                if m['ancho'] > 80:
                    st.light("💡 **Idea IA:** En este espacio largo, podrías añadir un 'Island Overlay' para una barra de desayuno.")
else:
    st.info("Utiliza el panel izquierdo para definir las medidas y secciones de tu mueble.")
    
