import os 
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Función para codificar imagen a base64
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Configuración inicial de la página
st.set_page_config(page_title='🎨 Tablero Creativo', layout="centered")

# Estilos visuales
st.markdown("""
    <style>
        html, body, [data-testid="stApp"] {
            background-color: #e0f7ff;
            color: #000000;
            font-family: 'Comic Sans MS', cursive, sans-serif;
        }
        .block-container {
            background-color: #e0f7ff !important;
        }
        h1, h3, h4, p, label, span {
            color: #000000 !important;
            text-align: center;
        }
        .stTextInput > div > div > input {
            text-align: center;
        }
        .stButton > button {
            background: linear-gradient(to right, #FFA726, #FB8C00);
            color: white;
            font-weight: bold;
            font-size: 16px;
            padding: 12px 24px;
            border-radius: 10px;
            display: block;
            margin: 0 auto;
            margin-top: 20px;
        }
        .stSlider {
            color: #000000 !important;
        }
        .centered-canvas {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Título y subtítulo
st.markdown("<h1>🎨 Tablero Creativo</h1>", unsafe_allow_html=True)
st.markdown("<h4>🖌️ ¡Dibuja lo que imagines y deja que la IA lo interprete!</h4>", unsafe_allow_html=True)

# Configuración del canvas
drawing_mode = "freedraw"
stroke_width = st.slider('✨ Elige el grosor del pincel', 1, 30, 10)
stroke_color = "#000000" 
bg_color = '#FFFDD0'  # crema suave

# Mostrar canvas
st.markdown('<div class="centered-canvas">', unsafe_allow_html=True)
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)
st.markdown('</div>', unsafe_allow_html=True)

# Input de API key
ke = st.text_input('🔐 Ingresa tu clave de OpenAI (GPT)')
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# Botón para analizar
analyze_button = st.button("🔍 Analiza tu dibujo")

# Análisis del dibujo
if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("🎯 Estoy observando tu creación..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")
        prompt_text = "Describe brevemente en español lo que ves en la imagen"

        try:
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
              max_tokens=500,
            )

            description = response.choices[0].message.content
            st.markdown("<h4>🧠 Esto es lo que veo en tu dibujo:</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 18px;'>{description}</p>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Ocurrió un error: {e}")
else:
    if not api_key:
        st.warning("🔑 Por favor, ingresa tu clave de API para comenzar.")
