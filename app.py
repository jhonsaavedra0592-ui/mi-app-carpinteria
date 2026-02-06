import streamlit as st
from PIL import Image, ImageDraw
import pandas as pd
from fpdf import FPDF
import tempfile

# Configuración de la página
st.set_page_config(page_title="Carpintería Pro", layout="wide")

st.title("🛠️ Sistema Universal de Carpintería")
st.write("Diseña módulos, calcula costos y genera tu presupuesto en PDF.")

# --- 1. CONFIGURACIÓN DE PRECIOS (Barra Lateral) ---
st.sidebar.header("Configuración de Negocio")
costo_hoja = st.sidebar.number_input("Precio Hoja Plywood (4x8)", value=55.0)
costo_herraje = st.sidebar.number_input("Herrajes por Módulo ($)", value=25.0)
mano_obra_pulg = st.sidebar.number_input("Mano de Obra (por pulgada de ancho)", value=12.0)
profundidad_std = st.sidebar.number_input("Profundidad (pulgadas)", value=23.25)

# --- 2. GESTIÓN DE MÓDULOS ---
if "modulos" not in st.session_state:
    st.session_state.modulos = []

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Añadir Módulo")
    with st.form("form_modulo"):
        nombre = st.text_input("Nombre del mueble", placeholder="Ej: Fregadero, Alacena...")
        ancho = st.number_input("Ancho (pulgadas)", min_value=1.0, value=24.0)
        alto = st.number_input("Alto (pulgadas)", min_value=1.0, value=34.5)
        btn_add = st.form_submit_button("➕ Agregar al diseño")
        
        if btn_add:
            st.session_state.modulos.append({
                "nombre": nombre if nombre else "Módulo",
                "ancho": ancho,
                "alto"
