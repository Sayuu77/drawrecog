import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Configuración de página
st.set_page_config(
    page_title="Tablero Inteligente",
    page_icon="🎨",
    layout="centered"
)

# Estilos minimalistas
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">🎨 Tablero Inteligente</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Dibuja y deja que la IA interprete tu boceto</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Configuración")
    
    with st.container():
        st.markdown("**Herramientas de dibujo**")
        stroke_width = st.slider('Ancho del trazo', 1, 20, 5)
        stroke_color = st.color_picker('Color del trazo', '#000000')
    
    with st.container():
        st.markdown("**🔑 API Key**")
        api_key = st.text_input('Ingresa tu clave de OpenAI', type='password')

    st.markdown("---")
    st.markdown("### ℹ️ Acerca de")
    st.markdown("Esta aplicación utiliza IA para interpretar bocetos dibujados a mano.")

# Área principal de dibujo
st.markdown("### Panel de Dibujo")
st.markdown('<div class="canvas-container">', unsafe_allow_html=True)

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color="#FFFFFF",
    height=400,
    width=600,
    drawing_mode="freedraw",
    key="canvas",
)

st.markdown('</div>', unsafe_allow_html=True)

# Botón de análisis
analyze_button = st.button("Analizar Boceto", type="primary", use_container_width=True)

# Procesamiento
if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("🔄 Analizando tu dibujo..."):
        try:
            # Procesar imagen
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
            input_image.save('img.png')
            
            # Codificar imagen
            base64_image = encode_image_to_base64("img.png")
            
            # Configurar API
            os.environ['OPENAI_API_KEY'] = api_key
            client = OpenAI(api_key=api_key)
            
            # Prompt para análisis
            prompt_text = "Describe brevemente en español qué representa este dibujo o boceto."
            
            # Llamada a la API
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )
            
            # Mostrar resultado
            if response.choices[0].message.content:
                st.markdown("### Interpretación")
                st.markdown('<div class="response-box">', unsafe_allow_html=True)
                st.write(response.choices[0].message.content)
                st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ Error en el análisis: {str(e)}")

elif analyze_button:
    if not api_key:
        st.warning("⚠️ Por favor ingresa tu API key de OpenAI en el panel lateral.")
    if canvas_result.image_data is None:
        st.info("🎨 Dibuja algo en el panel antes de analizar.")
