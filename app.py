import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from fpdf import FPDF
import tempfile

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Carpintería Pro - Cotizador", layout="wide")

# Inicializar la lista de módulos para que no dé error al recargar
if "modulos" not in st.session_state:
    st.session_state.modulos = []

st.title("🪚 Cotizador de Carpintería Profesional")

# --- 2. ENTRADA DE DATOS (BARRA LATERAL) ---
with st.sidebar:
    st.header("Configurar Módulo")
    nombre = st.text_input("Nombre del módulo", placeholder="Ej: Módulo Cocina")
    
    col_a, col_h = st.columns(2)
    with col_a:
        ancho = st.number_input("Ancho (pulg)", min_value=1.0, value=20.0)
    with col_h:
        alto = st.number_input("Alto (pulg)", min_value=1.0, value=30.0)
    
    st.divider()
    st.subheader("Costos y Mano de Obra")
    costo_hoja = st.number_input("Costo Hoja (48x96)", min_value=0.0, value=850.0)
    costo_herraje = st.number_input("Costo Herrajes", min_value=0.0, value=120.0)
    mano_obra_pulg = st.number_input("Mano de obra x pulgada", min_value=0.0, value=15.0)
    
    # --- LA SOLUCIÓN AL ERROR: Definir el botón antes del IF ---
    btn_add = st.button("➕ Agregar al Presupuesto")
    
    st.divider()
    if st.button("🗑️ Limpiar Todo"):
        st.session_state.modulos = []
        st.rerun()

# --- 3. LÓGICA DE CÁLCULO ---
if btn_add:
    # Cálculo basado en área de hoja estándar (48x96 pulg)
    area_hoja = 48 * 96
    area_frontal = ancho * alto
    costo_material = (area_frontal / area_hoja) * costo_hoja
    
    # Costo total de producción
    costo_total = costo_material + costo_herraje + (ancho * mano_obra_pulg)
    
    # Guardar en la lista
    st.session_state.modulos.append({
        "Módulo": nombre if nombre else f"Pieza {len(st.session_state.modulos)+1}",
        "Dimensiones": f"{ancho}\" x {alto}\"",
        "Ancho": ancho, # Guardamos numérico para el dibujo
        "Alto": alto,   # Guardamos numérico para el dibujo
        "Costo ($)": round(costo_total, 2)
    })
    st.success(f"✅ {nombre} agregado!")

# --- 4. VISUALIZACIÓN Y RESUMEN ---
if st.session_state.modulos:
    col_tabla, col_dibujo = st.columns([1, 1])
    df = pd.DataFrame(st.session_state.modulos)
    
    with col_tabla:
        st.subheader("📋 Lista de Módulos")
        st.dataframe(df[["Módulo", "Dimensiones", "Costo ($)"]], use_container_width=True)
        
        total_proyecto = df["Costo ($)"].sum()
        st.metric("Total Estimado", f"${total_proyecto:,.2f}")

    with col_dibujo:
        st.subheader("📐 Vista Previa")
        # Generar imagen dinámica
        img = Image.new('RGB', (800, 350), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        x_offset = 30
        
        for m in st.session_state.modulos:
            w, h = int(m["Ancho"] * 4), int(m["Alto"] * 4)
            # Dibujamos el mueble (café madera)
            draw.rectangle([x_offset, 300-h, x_offset+w, 300], outline="#5D4037", width=4, fill="#D2B48C")
            draw.text((x_offset, 310), m["Módulo"], fill="black")
            x_offset += w + 20
            
        st.image(img, use_container_width=True)

    # --- 5. EXPORTACIÓN A PDF ---
    st.divider()
    if st.button("📄 Generar PDF para Cliente"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "PRESUPUESTO DE TRABAJO", ln=True, align='C')
        
        pdf.set_font("Arial", '', 12)
        pdf.ln(10)
        for m in st.session_state.modulos:
            pdf.cell(0, 10, f"{m['Módulo']} ({m['Dimensiones']}): ${m['Costo ($)']}", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"TOTAL FINAL: ${sum(m['Costo ($)'] for m in st.session_state.modulos):,.2f}", ln=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                st.download_button("⬇️ Descargar Presupuesto", f, file_name="cotizacion.pdf")
else:
    st.info("👈 Comienza agregando un módulo en la barra lateral.")
 
