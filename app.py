import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Generador Universal de Carpintería", layout="wide")

if "proyecto" not in st.session_state:
    st.session_state.proyecto = []

st.title("🪚 Sistema Universal de Diseño de Mobiliario")
st.write("Crea planos técnicos para cocinas, baños, clósets o centros de entretenimiento.")

# --- 2. BARRA LATERAL: ENTRADA PARAMÉTRICA ---
with st.sidebar:
    st.header("⚙️ Parámetros del Mueble")
    
    muro = st.selectbox("Ubicación (Pared/Sección)", ["Sección 1", "Sección 2", "Sección 3"])
    
    # Categoría universal
    categoria = st.selectbox("Categoría de Mueble", 
                            ["Gabinete Bajo (Floor)", "Gabinete Alto (Wall)", "Torre (Full Height)", "Mueble Especial"])
    
    nombre = st.text_input("Etiqueta del mueble", "Ej. Vanitorio Baño")
    
    col1, col2 = st.columns(2)
    with col1:
        ancho = st.number_input("Ancho (in)", 5.0, 150.0, 24.0)
        prof = st.number_input("Profundidad (in)", 4.0, 48.0, 24.0)
    with col2:
        alto = st.number_input("Alto (in)", 5.0, 110.0, 34.5)
        espesor = st.selectbox("Material (in)", [0.5, 0.625, 0.75], index=2)

    st.divider()
    st.subheader("📐 Configuración Interna")
    tipo_division = st.radio("Tipo de frente/espacio", ["Cajonera", "Puertas", "Repisas Abiertas", "Espacio Libre"])
    num_div = st.slider("Cantidad de divisiones", 1, 12, 2)
    
    if st.button("➕ Insertar Mueble"):
        st.session_state.proyecto.append({
            "muro": muro, "nombre": nombre, "tipo": categoria,
            "ancho": ancho, "alto": alto, "prof": prof,
            "estilo": tipo_division, "div": num_div, "e": espesor
        })

    if st.button("🗑️ Vaciar Proyecto"):
        st.session_state.proyecto = []
        st.rerun()

# --- 3. MOTOR DE RENDERIZADO TÉCNICO UNIVERSAL ---
def dibujar_universo_mueble(modulos):
    ESC = 10 # Escala 1 pulgada = 10px
    total_w = sum(m['ancho'] for m in modulos)
    img_w = int(total_w * ESC) + 200
    img_h = 800
    
    img = Image.new('RGB', (img_w, img_h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    x_offset = 100
    piso_y = 700
    
    for m in modulos:
        w_px = int(m['ancho'] * ESC)
        h_px = int(m['alto'] * ESC)
        
        # Ajuste de posición según tipo (Los altos flotan, los bajos van al piso)
        if "Alto" in m['tipo']:
            y_base = 350 # Posición flotante para alacenas
        else:
            y_base = piso_y
            
        y_top = y_base - h_px
        
        # 1. Dibujar Estructura (Caja)
        draw.rectangle([x_offset, y_top, x_offset + w_px, y_base], outline="black", width=3)
        
        # 2. Lógica Universal de Divisiones
        if m['div'] > 0:
            if m['estilo'] == "Cajonera" or m['estilo'] == "Repisas Abiertas":
                espacio_h = h_px / m['div']
                for i in range(1, m['div']):
                    y_linea = y_top + (i * espacio_h)
                    draw.line([(x_offset, y_linea), (x_offset + w_px, y_linea)], fill="black", width=1)
                    if m['estilo'] == "Cajonera":
                        # Jaladera de cajón
                        draw.line([x_offset + w_px/2 - 15, y_linea - 10, x_offset + w_px/2 + 15, y_linea - 10], fill="black", width=3)
                # Jaladera final
                if m['estilo'] == "Cajonera":
                    draw.line([x_offset + w_px/2 - 15, y_base - 10, x_offset + w_px/2 + 15, y_base - 10], fill="black", width=3)
            
            elif m['estilo'] == "Puertas":
                # División vertical para puertas dobles
                draw.line([(x_offset + w_px/2, y_top), (x_offset + w_px/2, y_base)], fill="black", width=1)
                # Tiradores verticales
                draw.line([x_offset + w_px/2 - 5, y_top + 20, x_offset + w_px/2 - 5, y_top + 60], fill="black", width=2)
                draw.line([x_offset + w_px/2 + 5, y_top + 20, x_offset + w_px/2 + 5, y_top + 60], fill="black", width=2)

        # 3. Cotas y Etiquetas
        draw.text((x_offset + 5, y_top - 40), f"{m['nombre']}", fill="black")
        draw.text((x_offset + w_px/2 - 10, y_top - 20), f"{m['ancho']}\"", fill="red") # Cota Ancho
        draw.line([x_offset - 10, y_top, x_offset - 10, y_base], fill="blue", width=1) # Cota Alto
        draw.text((x_offset - 40, y_top + h_px/2), f"{m['alto']}\"", fill="blue")

        x_offset += w_px + 10
        
    return img

# --- 4. CÁLCULO DE DESPIECE UNIVERSAL ---
def generar_corte_universal(m):
    e = m['e']
    piezas = [
        {"Pieza": "Lateral Izq/Der", "Cant": 2, "Largo (in)": m['alto'], "Ancho (in)": m['prof']},
        {"Pieza": "Piso/Techo", "Cant": 2, "Largo (in)": m['ancho'] - (2*e), "Ancho (in)": m['prof']},
        {"Pieza": "Fondo (Backing)", "Cant": 1, "Largo (in)": m['alto'], "Ancho (in)": m['ancho']}
    ]
    if m['div'] > 1 and m['estilo'] != "Cajonera":
        piezas.append({"Pieza": "Repisas Internas", "Cant": m['div']-1, "Largo (in)": m['ancho'] - (2*e), "Ancho (in)": m['prof'] - 1})
    return pd.DataFrame(piezas)

# --- 5. INTERFAZ FINAL ---
if st.session_state.proyecto:
    tab1, tab2 = st.tabs(["🖼️ Plano General", "📋 Despiece para Taller"])
    
    with tab1:
        st.image(dibujar_universo_mueble(st.session_state.proyecto), use_container_width=True)
    
    with tab2:
        for i, m in enumerate(st.session_state.proyecto):
            with st.expander(f"Módulo {i+1}: {m['nombre']} ({m['ancho']}x{m['alto']})"):
                st.table(generar_corte_universal(m))
else:
    st.info("Configura un mueble en el panel izquierdo para generar planos y medidas automáticas.")
