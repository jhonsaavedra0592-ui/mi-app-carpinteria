import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from fpdf import FPDF
import tempfile

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Cotizador Carpintería", layout="wide")

# Inicializamos el almacén de datos (session_state) para que no se borren al recargar
if "modulos" not in st.session_state:
    st.session_state.modulos = []

st.title("🪚 Sistema de Cotización para Carpintería")

# 2. ENTRADA DE DATOS (En la barra lateral)
with st.sidebar:
    st.header("Datos del Módulo")
    nombre = st.text_input("Nombre del mueble/módulo", placeholder="Ej: Gabinete Cocina")
    ancho = st.number_input("Ancho (pulgadas)", min_value=1.0, value=20.0)
    alto = st.number_input("Alto (pulgadas)", min_value=1.0, value=30.0)
    
    st.divider()
    st.subheader("Costos de Materiales")
    costo_hoja = st.number_input("Precio de 1 hoja (4x8 ft)", min_value=0.0, value=800.0)
    costo_herraje = st.number_input("Costo de herrajes", min_value=0.0, value=150.0)
    mano_obra_pulg = st.number_input("Mano de obra (por pulgada)", min_value=0.0, value=15.0)

    # AQUÍ SE DEFINE LA VARIABLE btn_add PARA EVITAR EL ERROR
    btn_add = st.button("➕ Agregar Módulo")
    
    # Botón para reiniciar
    if st.button("🗑️ Borrar Todo"):
        st.session_state.modulos = []
        st.rerun()

# 3. LÓGICA DE CÁLCULOS (Solo ocurre cuando se presiona el botón definido arriba)
if btn_add:
    area_hoja = 48 * 96
    area_frontal = ancho * alto
    costo_material = (area_frontal / area_hoja) * costo_hoja
    costo_total = costo_material + costo_herraje + (ancho * mano_obra_pulg)
    
    # Guardamos los datos en la lista
    st.session_state.modulos.append({
        "Nombre": nombre if nombre else f"Módulo {len(st.session_state.modulos)+1}",
        "Ancho": ancho,
        "Alto": alto,
        "Costo": round(costo_total, 2)
    })
    st.success("¡Agregado correctamente!")

# 4. VISUALIZACIÓN Y PDF
col1, col2 = st.columns([1, 1])

if st.session_state.modulos:
    df = pd.DataFrame(st.session_state.modulos)
    
    with col1:
        st.subheader("📊 Resumen del Presupuesto")
        st.table(df)
        total = df["Costo"].sum()
        st.metric("Total del Proyecto", f"${total:,.2f}")

    with col2:
        st.subheader("🎨 Visualización Frontal")
        # Crear imagen base
        img = Image.new('RGB', (800, 300), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        x_offset = 20
        for m in st.session_state.modulos:
            w, h = int(m["Ancho"] * 4), int(m["Alto"] * 4)
            # Dibujar el rectángulo (módulo)
            draw.rectangle([x_offset, 250-h, x_offset+w, 250], outline="black", width=3, fill="#D2B48C")
            draw.text((x_offset + 5, 260), m["Nombre"], fill="black")
            x_offset += w + 10
        st.image(img, use_container_width=True)

    # 5. BOTÓN PARA PDF
    st.divider()
    if st.button("📄 Descargar Presupuesto en PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "COTIZACIÓN DE TRABAJO", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.ln(10)
        
        for m in st.session_state.modulos:
            texto = f"{m['Nombre']} - Dim: {m['Ancho']}x{m['Alto']} pulg. - Precio: ${m['Costo']}"
            pdf.cell(0, 10, texto, ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"TOTAL ESTIMADO: ${sum(m['Costo'] for m in st.session_state.modulos):,.2f}", ln=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                st.download_button("⬇️ Haz clic aquí para guardar tu PDF", f, file_name="presupuesto.pdf")
else:
    st.info("Configura las medidas a la izquierda y presiona 'Agregar Módulo'.")
    
