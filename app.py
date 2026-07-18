import streamlit as st
import os
import requests

# 1. Configuración de la página
st.set_page_config(page_title='Tutor LOGIA-UDP', layout='centered')

# Ocultar menús nativos de Streamlit para mejorar la estética
st.markdown("""<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem;}
</style>""", unsafe_allow_html=True)

# =========================================================================
# 📘 BARRA LATERAL: EL ENUNCIADO DEL CASO PARA EL ALUMNO
# =========================================================================
with st.sidebar:
    st.header("📘 Caso: Andina Logística SpA")
    st.write(
        "Andina Logística SpA opera un centro de distribución que durante las últimas "
        "cuatro semanas ha presentado quiebres de stock, atrasos de despacho y reclamos de clientes. "
        "Paralelamente, algunos productos mantienen inventarios elevados que aumentan los costos de almacenamiento."
    )
    
    st.subheader("🎯 Objetivos y Restricciones")
    st.markdown("""
    * **Restricción 1:** El presupuesto disponible solo permite priorizar acciones sobre **dos productos**.
    * **Restricción 2:** La meta institucional de nivel de servicio es **95%**.
    * **Restricción 3:** No se puede cambiar de proveedor durante el periodo analizado.
    """)
    
    st.subheader("📊 Datos del Inventario Actual")
    datos_inventario = {
        "Producto": ["A-101", "B-205", "C-330", "D-410", "E-525"],
        "Stock Act.": [320, 980, 150, 650, 1200],
        "Demanda Mens.": [900, 450, 720, 600, 300],
        "Lead Time (días)": [8, 12, 6, 15, 10],
        "Stock Seg.": [120, 90, 100, 160, 80],
        "Ped. Pendientes": [180, 0, 240, 100, 0],
        "Nivel Servicio": ["87%", "98%", "82%", "91%", "99%"]
    }
    st.table(datos_inventario)
    st.caption("Nota: Considerar un mes base de 30 días hábiles.")

# =========================================================================
# 🤖 CUERPO PRINCIPAL: CHAT INTERACTIVO CON LOGIA
# =========================================================================
st.title('🤖 Consola Interactive LOGIA-UDP')
st.caption("Análisis Operacional: Centro de Distribución Nodo Sur")

# Obtener la API Key de los Secrets de manera limpia
api_key = None
if "OPENAI_API_KEY" in st.secrets:
    secret_val = st.secrets["OPENAI_API_KEY"]
    if isinstance(secret_val, dict):
        api_key = secret_val.get("OPENAI_API_KEY", "")
    else:
        api_key = str(secret_val)
elif os.getenv("OPENAI_API_KEY"):
    api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    api_key = api_key.strip().replace('"', '').replace("'", "")

# Inicializar el historial de conversación en la sesión si no existe
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy LOGIA. Revisa los datos del caso en la barra de la izquierda y descríbeme con tus palabras: ¿Cuál es el principal problema operacional del caso CD Nodo Sur y qué evidencia lo demuestra?"}
    ]

# Mostrar los mensajes anteriores del chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Entrada de texto del alumno (Chat Input)
if user_input := st.chat_input("Escribe tu respuesta o análisis aquí..."):
    # Guardar y mostrar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    # Llamada directa a la API usando requests para evitar errores de librerías en Streamlit
    if api_key:
        try:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                system_prompt = (
                    "Eres LOGIA-UDP, un tutor inteligente de gestión logística para estudiantes universitarios. "
                    "Tu objetivo es guiar al estudiante a resolver el caso de Andina Logística SpA. "
                    "No des las respuestas directas. Haz preguntas orientadoras, evalúa sus argumentos y ayúdale a calcular o "
                    "deducir qué dos productos debe priorizar (A-101 y C-330 son los críticos por su bajo nivel de servicio y pedidos pendientes). "
                    "Sé cordial, profesional y adopta un rol puramente formativo."
                )
                
                # Construir los mensajes para la API
                api_messages = [{"role": "system", "content": system_prompt}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]
                
                # Petición HTTP directa a OpenAI
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": api_messages,
                    "temperature": 0.7
                }
                
                response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                
                if response.status_code == 200:
                    assistant_response = response.json()["choices"][0]["message"]["content"]
                    message_placeholder.write(assistant_response)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                else:
                    st.error(f"Error de la API de OpenAI (Código {response.status_code}): {response.text}")
                    
        except Exception as e:
            st.error(f"Error de conexión con el tutor: {e}")
    else:
        st.warning("⚠️ La API Key de OpenAI no está configurada. Por favor, revísala en los Secrets de Streamlit.")

# =========================================================================
# 📥 SECCIÓN FINAL: DESCARGA DE BITÁCORA
# =========================================================================
st.markdown("---")
try:
    with open("LOGIA_UDP_Caso_Alumno.xlsx", "rb") as file:
        st.download_button(
            label="📥 Descargar Bitácora de Trabajo (Obligatorio)",
            data=file,
            file_name="LOGIA_UDP_Caso_Alumno.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
except FileNotFoundError:
    st.error("⚠️ Falta el archivo LOGIA_UDP_Caso_Alumno.xlsx en GitHub.")
