import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import tempfile
import os

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Master Carpintería IA", layout="wide")

# Inicializar estados para evitar errores de carga
if "proyecto" not in st.session_state:
    st.session_state.proyecto = []
if "secciones_temp" not in st.session_state:
    st.session_state.secciones_temp = []

st.title("🚀 Sistema Universal de Diseño y Cotización")

# --- 2. MOTOR DE DIBUJO TÉCNICO PROFESIONAL ---
def dibujar_plano_maestro(mueble):
    ESC = 12  # Escala píxeles por pulgada
    ancho_px = int(mueble['ancho'] * ESC) + 250
    alto_px = 750
    img = Image.new('RGB', (ancho_px, alto_px), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    x_offset = 120
    piso_y = 600
    h_px = int(mueble['alto'] * ESC)
    y_top = piso_y - h_px
    
    # Dibujar contorno exterior
    draw.rectangle([x_offset, y_top, x_offset + mueble['ancho']*ESC, piso_y], outline="black", width=4)
    
    x_cursor = x_offset
    for sec in mueble['secciones']:
        w_sec_px = int(sec['ancho'] * ESC)
        
        # Dibujar módulo
        draw.rectangle([x_cursor, y_top, x_cursor + w_sec_px, piso_y], outline="black", width=2)
        
        # Divisiones internas según tipo
        if sec['div'] > 1:
            alto_div = h_px / sec['div']
            for i in range(1, int(sec['div'])):
                y_div = y_top + (i * alto_div)
                draw.line([(x_cursor, y_div), (x_cursor + w_sec_px, y_div)], fill="black", width=1)
                # Jaladera
                draw.line([x_cursor + w_sec_px/2 - 15, y_div - 8, x_cursor + w_sec_px/2 + 15, y_div - 8], fill="gray", width=3)

        # COTAS ROJAS (Medidas de secciones)
        draw.line([x_cursor + 2, piso_y + 30, x_cursor + w_sec_px - 2, piso_y + 30], fill="red", width=2)
        draw.text((x_cursor + w_sec_px/2 - 10, piso_y + 40), f"{sec['ancho']}\"", fill="red")
        
        # Etiqueta de texto
        draw.text((x_cursor + 5, y_top + 5), f"{sec['tipo']}", fill="black")
        x_cursor += w_sec_px

    # Cota de Altura
    draw.line([x_offset - 40, y_top, x_offset - 40, piso_y], fill="blue", width=2)
    draw.text((x_offset - 90, y_top + h_px/2), f"{mueble['alto']}\"", fill="blue")
    
    # Cota Total
    draw.line([x_offset, piso_y + 100, x_offset + mueble['ancho']*ESC, piso_y + 100], fill="red", width=3)
    draw.text((x_offset + (mueble['ancho']*ESC)/2 - 30, piso_y + 110), f"TOTAL: {mueble['ancho']} in", fill="red")
    
    return img

# --- 3. FUNCIÓN DE PDF ---
def generar_pdf(mueble, imagen, costo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="REPORTE TÉCNICO DE DISEÑO", ln=True, align='C')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        imagen.save(tmp.name)
        pdf.image(tmp.name, x=10, y=30, w=190)
        tmp_path = tmp.name
    
    pdf.set_y(150)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(200, 10, txt=f"PRECIO ESTIMADO: ${costo:,.2f}", ln=True, align='R')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Configuración del Proyecto:", ln=True)
    for s in mueble['secciones']:
        pdf.cell(200, 7, txt=f"- Módulo {s['tipo']}: {s['ancho']} pulgadas.", ln=True)
    
    pdf_out = pdf.output(dest='S').encode('latin-1')
    os.unlink(tmp_path)
    return pdf_out

# --- 4. INTERFAZ DE USUARIO ---
with st.sidebar:
    st.header("📐 Configuración del Mueble")
    nombre_m = st.text_input("Nombre del Proyecto", "Cocina Moderna")
    ancho_t = st.number_input("Ancho Total (in)", 10.0, 300.0, 96.0)
    alto_t = st.number_input("Alto Total (in)", 10.0, 120.0, 36.0)
    precio_in = st.number_input("Precio por pulgada ($)", 5.0, 100.0, 15.0)

    st.divider()
    st.subheader("🧩 Agregar Sección")
    ancho_s = st.number_input("Ancho Sección", 5.0, 120.0, 24.0)
    tipo_s = st.selectbox("Tipo", ["Cajonera", "Puertas", "Fregadero", "Basura", "DW", "Espacio Libre"])
    divs_s = st.number_input("Divisiones", 1, 8, 3)
    
    if st.button("➕ Añadir Sección"):
        acumulado = sum(s['ancho'] for s in st.session_state.secciones_temp)
        if acumulado + ancho_s <= ancho_t:
            st.session_state.secciones_temp.append({"ancho": ancho_s, "tipo": tipo_s, "div": divs_s})
        else:
            st.error("Excede el ancho total.")

    if st.button("💾 Guardar y Diseñar"):
        st.session_state.proyecto.append({
            "nombre": nombre_m, "ancho": ancho_t, "alto": alto_t,
            "secciones": st.session_state.secciones_temp
        })
        st.session_state.secciones_temp = []
        st.rerun()

    if st.button("🗑️ Reset"):
        st.session_state.proyecto = []
        st.rerun()

# --- 5. VISUALIZACIÓN ---
if st.session_state.proyecto:
    for m in st.session_state.proyecto:
        with st.container(border=True):
            costo_final = (m['ancho'] * precio_in) + 200
            st.subheader(f"📋 {m['nombre']}")
            
            c1, c2 = st.columns([3, 1])
            with c1:
                img_p = dibujar_plano_maestro(m)
                st.image(img_p, use_container_width=True)
            with c2:
                st.metric("Presupuesto", f"${costo_final:,.2f}")
                pdf_data = generar_pdf(m, img_p, costo_final)
                st.download_button("📥 Descargar PDF", pdf_data, f"{m['nombre']}.pdf", "application/pdf")
                st.success("✅ Diseño optimizado por IA")
else:
    st.info("Configura las medidas a la izquierda para generar el plano profesional.")
    
