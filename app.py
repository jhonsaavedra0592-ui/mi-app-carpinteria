import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
import tempfile

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Carpintería Pro: Master Design", layout="wide")

if "proyecto" not in st.session_state:
    st.session_state.proyecto = []

st.title("🚀 Sistema Integral de Diseño, Despiece y Nesting")

# --- PARÁMETROS DE MATERIAL ---
ANCHO_HOJA = 96  # pulgadas
ALTO_HOJA = 48   # pulgadas
ESCALA_NESTING = 8 # Píxeles por pulgada para el gráfico de corte

# --- 2. HERRAMIENTAS DE DISEÑO ---
with st.sidebar:
    st.header("Configurador de Mueble")
    muro = st.selectbox("Asignar a Pared/Muro", ["Pared A (Principal)", "Pared B (Lateral)", "Isla"])
    tipo = st.selectbox("Tipo de Mueble", ["Gabinete Bajo", "Alacena Superior", "Torre Despensa", "Cajonera"])
    
    ancho = st.number_input("Ancho (in)", 5.0, 120.0, 30.0)
    alto = st.number_input("Alto (in)", 10.0, 120.0, 34.5)
    prof = st.number_input("Profundidad (in)", 10.0, 30.0, 24.0)
    
    div = st.slider("Número de divisiones", 1, 6, 2)
    espesor = st.selectbox("Espesor del material (in)", [0.5, 0.625, 0.75], index=2)

    if st.button("➕ Agregar al Proyecto"):
        st.session_state.proyecto.append({
            "muro": muro, "tipo": tipo, "ancho": ancho, 
            "alto": alto, "prof": prof, "div": div, "espesor": espesor
        })

    if st.button("🗑️ Reiniciar Todo"):
        st.session_state.proyecto = []
        st.rerun()

# --- 3. LÓGICA DE DESPIECE Y OPTIMIZACIÓN ---
def calcular_despiece(m):
    e = m['espesor']
    piezas = [
        {"Pieza": "Lateral", "Largo": m['alto'], "Ancho": m['prof'], "Cant": 2},
        {"Pieza": "Piso/Techo", "Largo": m['ancho'] - (2*e), "Ancho": m['prof'], "Cant": 2},
        {"Pieza": "Fondo", "Largo": m['alto'], "Ancho": m['ancho'], "Cant": 1},
    ]
    if m['div'] > 1:
        piezas.append({"Pieza": "Repisa", "Largo": m['ancho'] - (2*e) - 0.1, "Ancho": m['prof'] - 1, "Cant": m['div']-1})
    return piezas

def optimizar_nesting(todas_piezas):
    """Algoritmo simple de empaquetado por estantería (Shelf Packing)"""
    piezas_individuales = []
    for p in todas_piezas:
        for _ in range(p['Cant']):
            # Orientamos siempre el lado largo en el eje X para consistencia
            ancho_p, alto_p = (p['Largo'], p['Ancho']) if p['Largo'] >= p['Ancho'] else (p['Ancho'], p['Largo'])
            piezas_individuales.append({'w': ancho_p, 'h': alto_p, 'nombre': p['Pieza']})
    
    # Ordenar por altura descendente
    piezas_individuales.sort(key=lambda x: x['h'], reverse=True)

    hojas = []
    def nueva_hoja(): return {"piezas": [], "x": 0, "y": 0, "h_max_fila": 0}
    
    hoja_actual = nueva_hoja()
    for p in piezas_individuales:
        # Si la pieza no cabe en la fila actual, saltar a la siguiente
        if hoja_actual['x'] + p['w'] > ANCHO_HOJA:
            hoja_actual['x'] = 0
            hoja_actual['y'] += hoja_actual['h_max_fila']
            hoja_actual['h_max_fila'] = 0
        
        # Si no cabe en la hoja actual, crear nueva hoja
        if hoja_actual['y'] + p['h'] > ALTO_HOJA:
            hojas.append(hoja_actual)
            hoja_actual = nueva_hoja()
        
        # Colocar pieza
        hoja_actual['piezas'].append({'x': hoja_actual['x'], 'y': hoja_actual['y'], 'w': p['w'], 'h': p['h'], 'n': p['nombre']})
        hoja_actual['x'] += p['w']
        hoja_actual['h_max_fila'] = max(hoja_actual['h_max_fila'], p['h'])
    
    hojas.append(hoja_actual)
    return hojas

# --- 4. VISUALIZACIÓN ---
if st.session_state.proyecto:
    tab_planos, tab_despiece, tab_nesting = st.tabs(["🖼️ Planos", "📋 Despiece", "📐 Optimización (Nesting)"])
    
    with tab_planos:
        muros = sorted(list(set(m['muro'] for m in st.session_state.proyecto)))
        for m_nombre in muros:
            st.subheader(f"📍 {m_nombre}")
            modulos_muro = [m for m in st.session_state.proyecto if m['muro'] == m_nombre]
            img = Image.new('RGB', (int(sum(m['ancho'] for m in modulos_muro) * 8 + 100), 400), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            x_off = 50
            for mod in modulos_muro:
                w, h = int(mod['ancho'] * 8), int(mod['alto'] * 8)
                draw.rectangle([x_off, 350-h, x_off+w, 350], outline="black", width=2, fill="#F1F1F1")
                draw.text((x_off+5, 350-h+5), f"{mod['ancho']}\"", fill="blue")
                x_off += w + 10
            st.image(img)

    with tab_despiece:
        total_piezas_proyecto = []
        for i, m in enumerate(st.session_state.proyecto):
            piezas = calcular_despiece(m)
            total_piezas_proyecto.extend(piezas)
            with st.expander(f"Módulo {i+1}: {m['tipo']}"):
                st.table(pd.DataFrame(piezas))

    with tab_nesting:
        st.subheader("Optimización de Corte en Hojas de 4x8 ft")
        hojas_finales = optimizar_nesting(total_piezas_proyecto)
        st.info(f"Se requieren **{len(hojas_finales)}** hojas de material.")

        for i, hoja in enumerate(hojas_finales):
            st.write(f"**Hoja #{i+1}**")
            # Dibujar mapa de corte
            img_h = Image.new('RGB', (ANCHO_HOJA * ESCALA_NESTING, ALTO_HOJA * ESCALA_NESTING), (240, 240, 240))
            draw_h = ImageDraw.Draw(img_h)
            for p in hoja['piezas']:
                coords = [p['x']*ESCALA_NESTING, p['y']*ESCALA_NESTING, (p['x']+p['w'])*ESCALA_NESTING, (p['y']+p['h'])*ESCALA_NESTING]
                draw_h.rectangle(coords, outline="black", fill="#D2B48C", width=2)
                draw_h.text((p['x']*ESCALA_NESTING+5, p['y']*ESCALA_NESTING+5), f"{p['w']}x{p['h']}", fill="black")
            st.image(img_h, use_container_width=True)

else:
    st.info("👈 Agrega muebles para generar los planos y el nesting automáticamente.")
                
