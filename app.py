import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title='Tutor LOGIA-UDP', layout='compact')

# Ocultar menús nativos de Streamlit para mejorar la estética en Canvas
st.markdown("""<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem;}
</style>""", unsafe_allow_html=True)

st.title('🤖 Consola Interactiva LOGIA-UDP')
st.caption('Análisis Operacional: Centro de Distribución Nodo Sur')

PROMPT_MAESTRO = """Eres LOGIA, un tutor formativo de Ingeniería en la Industria y Logística UDP.
Tu propósito es guiar al estudiante en el caso CD Nodo Sur. Nunca entregues la respuesta final ni calcules por él."""

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {'role': 'system', 'content': PROMPT_MAESTRO},
        {'role': 'assistant', 'content': '¡Hola! Soy LOGIA. Descríbeme con tus palabras: ¿Cuál es el principal problema operacional del caso CD Nodo Sur?'}
    ]

for msg in st.session_state.messages:
    if msg['role'] != 'system':
        with st.chat_message(msg['role']):
            st.write(msg['content'])

if user_input := st.chat_input('Escribe tu análisis operativo aquí...'):
    st.session_state.messages.append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.write(user_input)
        
    try:
        client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=st.session_state.messages,
            temperature=0.5
        )
        respuesta_ia = response.choices[0].message.content
    except Exception as e:
        respuesta_ia = f'⚠️ Error de conexión con el servidor de IA: {str(e)}'

    st.session_state.messages.append({'role': 'assistant', 'content': respuesta_ia})
    with st.chat_message('assistant'):
        st.write(respuesta_ia)

st.divider()
bitacora_texto = 'BITÁCORA DE TRABAJO — LOGIA-UDP\n=======================================\n\n'
for msg in st.session_state.messages:
    if msg['role'] != 'system':
        autor = 'ESTUDIANTE' if msg['role'] == 'user' else 'TUTOR LOGIA'
        bitacora_texto += f'[{autor}]: {msg["content"]}\n\n'

st.download_button(label='📥 Descargar Bitácora de Trabajo (Obligatorio)', data=bitacora_texto, file_name='bitacora_tutor_LOGIA.txt', mime='text/plain', use_container_width=True)