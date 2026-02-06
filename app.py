import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Carpintería Pro: IA Design", layout="wide")

if "proyecto" not in st.session_state:
    st.session_state.proyecto = []

# --- MOTOR DE INTELIGENCIA DE DISEÑO (LÓGICA DE IA) ---
def generar_sugerencia_ia(ancho_total, alto):
    """Analiza las medidas y propone una configuración lógica"""
    sugerencias = []
    
    if ancho_total >= 90:
        sugerencias.append({
            "estilo": "Cocina Profesional",
            "descripcion": "En este espacio de +90\", lo ideal es un combo de: 1 Basurero (18\"), 1 Cajonera Grande (30\"), 1 Fregadero (36\") y Lavavajillas.",
            "secciones": [
                {"ancho": 18, "tipo": "Basura", "div": 1},
                {"ancho": 30, "tipo": "Cajonera", "div": 3},
                {"ancho": 34, "tipo": "Fregadero", "div": 2},
                {"ancho": 24, "tipo": "DW", "div": 1}
            ]
        })
    
    if 40 <= ancho_total < 90:
        sugerencias.append({
            "estilo": "Vanity de Baño Moderno",
            "descripcion": "Para un espacio mediano, una sección de puertas central con cajones laterales maximiza el almacenaje.",
            "secciones": [
                {"ancho": ancho_total * 0.3, "tipo": "Cajones", "div": 3},
                {"ancho": ancho_total * 0.4, "tipo": "Puertas", "div": 2},
                {"ancho": ancho_total * 0.3, "tipo": "Cajones", "div": 3}
            ]
        })

    if alto > 80:
        sugerencias.append({
            "estilo": "Torre de Despensa / Clóset",
            "descripcion": "Debido a la gran altura, te sugiero dividir en 3 secciones: Maletero superior, Espacio de colgado y Cajones inferiores.",
            "secciones": [
                {"ancho": ancho_total, "tipo": "Maletero", "div": 1},
                {"ancho": ancho_total, "tipo": "Cajonera", "div": 4}
            ]
        })
    
    return sugerencias

# --- INTERFAZ DE USUARIO ---
st.title("🤖 Carpintería Pro + IA de Diseño")

with st.sidebar:
    st.header("📏 Medidas del Espacio")
    ancho_vacio = st.number_input("Ancho disponible (in)", 10.0, 300.0, 96.0)
    alto_vacio = st.number_input("Alto disponible (in)", 10.0, 120.0, 36.0)
    
    if st.button("🧠 Generar Ideas con IA"):
        st.session_state.ideas_ia = generar_sugerencia_ia(ancho_vacio, alto_vacio)

# --- MOSTRAR SUGERENCIAS DE IA ---
if "ideas_ia" in st.session_state:
    st.subheader("💡 Sugerencias de Diseño para tu Medida")
    cols = st.columns(len(st.session_state.ideas_ia))
    
    for idx, idea in enumerate(st.session_state.ideas_ia):
        with cols[idx]:
            st.info(f"**{idea['estilo']}**")
            st.write(idea['descripcion'])
            if st.button(f"Aplicar Diseño {idx+1}"):
                st.session_state.proyecto.append({
                    "nombre": idea['estilo'],
                    "ancho": ancho_vacio,
                    "alto": alto_vacio,
                    "secciones": idea['secciones']
                })
                st.rerun()

# --- (Aquí iría tu función de dibujo 'dibujar_plano_detallado' que ya creamos) ---
