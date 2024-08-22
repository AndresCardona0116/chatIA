import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
import os

st.sidebar.markdown(
    """
    <style>
    .custom-button {
        display: inline-block;
        padding: 0.5em 1em;
        color: #1722FF !important;
        border-radius: 50px;
        background-color: #FFD117;
        text-align: center;
        cursor: pointer;
        text-decoration: none;
        width: 100%;
        font-size: 20px;
        font-family: "Roboto";
        transition-duration: 0.2s;
        border-width: 2px 2px 2px 2px;
        border-style: solid;
        border-color: #FFD117;
        margin-top: 40px;
    }
    
    .custom-button:hover {
        background-color: #f0f0f0;
        text-decoration: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Configuración de la aplicación
st.title("💙 DomiAssistant 💙")

# Configuración de OAuth2
CLIENT_SECRETS_FILE = "./client_secret.json"  # Asegúrate de que la ruta es correcta
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
REDIRECT_URI = 'http://localhost:8501/'
project_id = "domina-bi"

def authenticate_user():
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        auth_url, _ = flow.authorization_url(prompt='consent')

        # Captura el código de autorización desde los parámetros de consulta
        query_params = st.query_params
        code = query_params.get("code")

        if code:
            flow.fetch_token(code=code)
            creds = flow.credentials

            # Guardar las credenciales en sesión
            st.session_state.credentials = creds

            st.success("Autenticación exitosa. Ahora puedes hacer preguntas.")
            st.experimental_set_query_params()  # Limpia los parámetros de consulta
        else:
            st.write(f"Por favor, sigue este enlace para autenticarte: [Autenticación]({auth_url})")

    except Exception as e:
        print(f'Error en la autenticación: {e}')

def generate_response(prompt):
    try:
        # Verificar si las credenciales están en la sesión
        if "credentials" not in st.session_state:
            st.error("No estás autenticado. Por favor, autentícate primero.")
            return

        creds = st.session_state.credentials

        # Inicializa Vertex AI usando las credenciales autenticadas
        vertexai.init(project=project_id, location="us-central1", credentials=creds)
        model = GenerativeModel(
            "gemini-1.5-flash-001",
            system_instruction=[
                "Eres un agente de Domina Entrega Total, llamado Dom-IA y siempre en tu primer interacción te presentaras como agente de productividad de Domina y tu nombre.",
                "debes dar respuestas concretas y enfocadas en un mundo corporativo y guiando al usuario siempre en alcanzar mejor productividad en tus tareas diarias.",
                "principalmente estarás recibiendo correos electrónicos para resumir y responder. También tendrás el reto de ayudar a las personas a acceder a conocimientos generales de forma mas rápida y sencilla",
                "cuando recibas documentos, audios o fotos inicia presentandote y da una respuesta donde primero tenga un resumen general con las conclusiones mas importantes",
                "en ocasiones, interactuarás con desarrolladores que te harán preguntas a nivel de código. Siempre prioriza las mejores prácticas y utiliza tecnologías actualizadas en el mercado para brindar respuestas precisas y efectivas."
            ],
        )
        chat = model.start_chat()

        # Configuración del modelo
        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        }

        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        # Generar respuesta
        response = chat.send_message(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        
        st.sidebar.success(model.count_tokens(prompt))

        return response.text

    except Exception as e:
        st.error(f"Error al obtener la respuesta: {e}")
        return "No se pudo obtener una respuesta en este momento."

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes de chat del historial en la aplicación
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.sidebar.title("💙 Dom-IA 💙")

# Autenticación del usuario
if "credentials" not in st.session_state:
    if st.sidebar.markdown('<a href="#" class="custom-button">Autenticar con Google</a>', unsafe_allow_html=True):
        authenticate_user()

if "credentials" in st.session_state:
    if (prompt := st.chat_input("¿Qué dudas tienes?")):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = generate_response(prompt)
            st.markdown("💙 Dom-IA 💙")
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.warning("Por favor, autentícate con Google para continuar.", icon="⚠")
