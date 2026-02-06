import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from fpdf import FPDF
import tempfile

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Carpintería Pro - Diseñador", layout="wide")

if "modulos" not in st.session_state:
    st.session_state.modulos = []

st.title("🪚 Diseñador de Gabinetes Profesional")

# --- 2. ENTRADA DE DATOS (BARRA LATERAL) ---
with st.sidebar:
    st.header("Configurar Mueble")
    nombre = st.text_input("Nombre del Módulo", "Cocina")
    ancho = st.number_input("Ancho (pulg)", 1.0, 150.0, 30.0)
    alto = st.number_input("Alto (pulg)", 1.0, 150.0, 36.0)
    
    st.divider()
    st.subheader("Diseño Interno")
    # Esta es la clave para las divisiones
    num_div = st.number_input("Número de divisiones/cajones", 1, 12, 3)
    tipo_diseno = st.radio("Tipo de diseño", ["Cajones", "Espacios Abiertos"])
    
    st.divider()
    st.subheader("Costos")
    costo_hoja = st.number_input("Costo Hoja Triplay", value=800.0)
    mano_obra = st.number_input("Mano de obra x pulgada", value=15.0)
    
    btn_add = st.button("➕ Agregar al Proyecto")
    
    if st.button("🗑️ Limpiar Todo"):
        st.session_state.modulos = []
        st.rerun()

# --- 3. LÓGICA DE CÁLCULO ---
if btn_add:
    area_frontal = ancho * alto
    costo_mat = (area_frontal / (48*96)) * costo_hoja
    # Un pequeño extra por cada división interna
    total = costo_mat + (num_div * 50) + (ancho * mano_obra)
    
    st.session_state.modulos.append({
        "Nombre": nombre,
        "Ancho": ancho,
        "Alto": alto,
        "Divisiones": num_div,
        "Tipo": tipo_diseno,
        "Costo": round(total, 2)
    })
    st.success(f"✅ {nombre} agregado!")

# --- 4. VISUALIZACIÓN DETALLADA ---
if st.session_state.modulos:
    col_t, col_v = st.columns([1, 1.5])
    
    with col_t:
        st.subheader("📋 Resumen")
        df = pd.DataFrame(st.session_state.modulos)
        st.dataframe(df[["Nombre", "Divisiones", "Tipo", "Costo"]], use_container_width=True)
        st.metric("Inversión Total", f"${df['Costo'].sum():,.2f}")

    with col_v:
        st.subheader("📐 Vista Previa del Diseño")
        # Lienzo para el dibujo
        img = Image.new('RGB', (800, 400), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        x_off = 50
        for m in st.session_state.modulos:
            # Escala para el dibujo
            w_px = int(m["Ancho"] * 4)
            h_px = int(m["Alto"] * 4)
            y_base = 350
            y_techo = y_base - h_px
            
            # 1. Dibujar contorno del mueble
            draw.rectangle([x_off, y_techo, x_off + w_px, y_base], 
                           outline="#5D4037", width=4, fill="#D2B48C")
            
            # 2. Dibujar las divisiones internas
            if m["Divisiones"] > 1:
                alto_seccion = h_px / m["Divisiones"]
                for i in range(1, m["Divisiones"]):
                    y_linea = y_techo + (i * alto_seccion)
                    # Línea divisoria
                    draw.line([(x_off, y_linea), (x_off + w_px, y_linea)], 
                              fill="#5D4037", width=2)
                    
                    # Si son cajones, dibujamos una jaladera en cada sección
                    if m["Tipo"] == "Cajones":
                        cent_x = x_off + (w_px / 2)
                        cent_y = y_linea - (alto_seccion / 2)
                        draw.ellipse([cent_x-10, cent_y-2, cent_x+10, cent_y+2], fill="black")
                
                # Jaladera del último compartimento
                if m["Tipo"] == "Cajones":
                    cent_x = x_off + (w_px / 2)
                    cent_y = y_base - (alto_seccion / 2)
                    draw.ellipse([cent_x-10, cent_y-2, cent_x+10, cent_y+2], fill="black")

            draw.text((x_off, y_base + 10), m["Nombre"], fill="black")
            x_off += w_px + 40
            
        st.image(img, use_container_width=True)
else:
    st.info("Configura un módulo y presiona 'Agregar' para ver el diseño.")
            
