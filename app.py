import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
from fpdf import FPDF
import tempfile

# Nota: Asegúrate de tener definidas las variables: 
# ancho, alto, costo_hoja, costo_herraje, mano_obra_pulg, nombre

if btn_add:
    # 1. Cálculo de costo simple
    area_hoja = 48 * 96
    area_frontal = ancho * alto
    costo_material = (area_frontal / area_hoja) * costo_hoja
    costo_total = costo_material + costo_herraje + (ancho * mano_obra_pulg)
    
    # 2. Guardar en la lista de módulos
    st.session_state.modulos.append({
        "nombre": nombre if nombre else f"Módulo {len(st.session_state.modulos)+1}",
        "ancho": ancho,
        "alto": alto,
        "costo": round(costo_total, 2)
    })
    st.success("¡Módulo agregado!")

# --- 3. VISUALIZACIÓN Y CÁLCULOS ---
# (Asegúrate de que 'col2' esté definido antes con col1, col2 = st.columns(2))
with col2:
    st.header("Vista Previa y Resumen")
    if st.session_state.modulos:
        df = pd.DataFrame(st.session_state.modulos)
        st.table(df)
        
        total_proyecto = df["costo"].sum()
        st.metric("Inversión Total Estimada", f"${total_proyecto:,.2f}")

        # Dibujo simple del frente del mueble
        img = Image.new('RGB', (800, 300), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        x_offset = 20
        for m in st.session_state.modulos:
            # Escalar dimensiones para visualización
            w, h = m["ancho"] * 3, m["alto"] * 3
            draw.rectangle([x_offset, 250-h, x_offset+w, 250], outline="black", width=3, fill="#D2B48C")
            draw.text((x_offset + 5, 255), m["nombre"], fill="black")
            x_offset += w + 10
        
        st.image(img, caption="Esquema frontal del proyecto")

# --- 4. EXPORTACIÓN A PDF ---
if st.session_state.modulos:
    # Calculamos el total nuevamente para el PDF
    total_proyecto = sum(m["costo"] for m in st.session_state.modulos)
    
    if st.button("📄 Generar Presupuesto PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "Presupuesto de Carpintería Pro", ln=True, align='C')
        
        pdf.set_font("Arial", '', 12)
        pdf.ln(10)
        for m in st.session_state.modulos:
            pdf.cell(0, 10, f"{m['nombre']}: {m['ancho']}\"x{m['alto']}\" - ${m['costo']}", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"TOTAL: ${total_proyecto:,.2f}", ln=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                st.download_button("⬇️ Descargar PDF", f, file_name="presupuesto.pdf")

# Botón para limpiar proyecto
if st.sidebar.button("🗑️ Borrar Todo"):
    st.session_state.modulos = []
    st.rerun()
        
