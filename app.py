import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw

# --- CONFIGURACIÓN DE PANTALLA ---
st.set_page_config(page_title="Diseñador de Gabinetes Pro", layout="wide")

if "proyecto" not in st.session_state:
    st.session_state.proyecto = []

st.title("📏 Generador de Gabinetes por Secciones")

# --- BARRA LATERAL: DISEÑO POR MEDIDAS ---
with st.sidebar:
    st.header("1. Definir Mueble Principal")
    nombre_mueble = st.text_input("Nombre del mueble", "Cocina Principal")
    ancho_total = st.number_input("Ancho Total (in)", 5.0, 200.0, 96.0)
    alto_mueble = st.number_input("Alto (in)", 10.0, 100.0, 36.0)
    
    st.divider()
    st.header("2. Agregar Secciones Internas")
    st.info("Divide el ancho total en partes (Ej: 18, 20, 34, 24)")
    
    # Sistema para ir agregando pedazos al mueble
    if "secciones_temp" not in st.session_state:
        st.session_state.secciones_temp = []
    
    col1, col2 = st.columns(2)
    with col1:
        ancho_sec = st.number_input("Ancho Sección", 5.0, 100.0, 18.0)
        tipo_sec = st.selectbox("Tipo", ["Cajones", "Puerta", "Fregadero", "Basura", "DW"])
    with col2:
        div_sec = st.number_input("Divisiones", 1, 6, 1)
        if st.button("➕ Añadir Sección"):
            ancho_acumulado = sum(s['ancho'] for s in st.session_state.secciones_temp)
            if ancho_acumulado + ancho_sec <= ancho_total:
                st.session_state.secciones_temp.append({
                    "ancho": ancho_sec, "tipo": tipo_sec, "div": div_sec
                })
            else:
                st.error("¡Excede el ancho total!")

    # Mostrar lo que llevamos diseñado
    if st.session_state.secciones_temp:
        st.write("---")
        st.write("**Estructura actual:**")
        for s in st.session_state.secciones_temp:
            st.text(f"| {s['tipo']} ({s['ancho']}\")")
        
        if st.button("💾 Guardar Mueble Completo"):
            st.session_state.proyecto.append({
                "nombre": nombre_mueble,
                "ancho": ancho_total,
                "alto": alto_mueble,
                "secciones": st.session_state.secciones_temp
            })
            st.session_state.secciones_temp = [] # Limpiar para el siguiente
            st.rerun()

# --- MOTOR DE DIBUJO CON COTAS (ESTILO IMAGEN) ---
def dibujar_plano_detallado(mueble):
    ESC = 10 
    img_w = int(mueble['ancho'] * ESC) + 200
    img_h = 600
    img = Image.new('RGB', (img_w, img_h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    x_start = 100
    y_piso = 500
    h_px = int(mueble['alto'] * ESC)
    y_top = y_piso - h_px
    
    # 1. Dibujar Marco Exterior Total
    draw.rectangle([x_start, y_top, x_start + mueble['ancho']*ESC, y_piso], outline="black", width=3)
    
    # 2. Dibujar Secciones y Cotas
    x_actual = x_start
    for sec in mueble['secciones']:
        w_sec_px = int(sec['ancho'] * ESC)
        
        # Dibujar división vertical
        draw.rectangle([x_actual, y_top, x_actual + w_sec_px, y_piso], outline="black", width=2)
        
        # Dibujar divisiones internas (Cajones)
        if sec['div'] > 1:
            h_div = h_px / sec['div']
            for i in range(1, int(sec['div'])):
                y_ln = y_top + (i * h_div)
                draw.line([(x_actual, y_ln), (x_actual + w_sec_px, y_ln)], fill="black", width=1)
                # Jaladera
                draw.line([x_actual + w_sec_px/2 - 10, y_ln - 5, x_actual + w_sec_px/2 + 10, y_ln - 5], fill="gray", width=2)

        # 3. COTAS ROJAS (Medidas como en tu referencia)
        # Línea de cota inferior
        draw.line([x_actual + 2, y_piso + 20, x_actual + w_sec_px - 2, y_piso + 20], fill="red", width=1)
        # Texto de medida
        draw.text((x_actual + w_sec_px/2 - 5, y_piso + 25), f"{sec['ancho']}", fill="red")
        # Nombre de la sección
        draw.text((x_actual + 5, y_top + 5), sec['tipo'], fill="black")
        
        x_actual += w_sec_px

    # Cota de Alto
    draw.line([x_start - 20, y_top, x_start - 20, y_piso], fill="red", width=1)
    draw.text((x_start - 50, y_top + h_px/2), f"{mueble['alto']}\"", fill="red")
    
    # Cota Total
    draw.line([x_start, y_piso + 60, x_start + mueble['ancho']*ESC, y_piso + 60], fill="red", width=2)
    draw.text((x_start + (mueble['ancho']*ESC)/2, y_piso + 70), f"Total {mueble['ancho']} inches", fill="red")

    return img

# --- VISUALIZACIÓN ---
if st.session_state.proyecto:
    for m in st.session_state.proyecto:
        st.subheader(f"📋 Plano: {m['nombre']}")
        img_final = dibujar_plano_detallado(m)
        st.image(img_final, use_container_width=True)
else:
    st.info("Configura las secciones de tu mueble en el panel izquierdo.")
    
