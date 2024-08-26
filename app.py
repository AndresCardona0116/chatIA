import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content
import vertexai.preview.generative_models as generative_models
import os
import json

st.set_page_config(
    page_title="Dom-IA",
    page_icon="https://i.ibb.co/Gd2dRQj/Microsoft-Teams-image-2.png"  # URL a la imagen del ícono
)

# CSS para fijar el botón al final del sidebar y hacer scroll en los chats
st.markdown(
    """
    <style>
    
    .custom-content-buttom {
        width: 100%;
        text-align: center;
    }
    
    
    .custom-button {
        display: inline-block;
        padding: 0.5em 1em;
        color: #1722FF !important;
        border-radius: 10px;
        background-color: #FFD117;
        text-align: center;
        cursor: pointer;
        text-decoration: none;
        width: 70%;
        font-size: 15px;
        font-family: "Roboto";
        transition-duration: 0.2s;
        border-width: 2px 2px 2px 2px;
        border-style: solid;
        border-color: #FFD117;
        margin-top: 5%;
        font-weight: bold;
    }
    
    .custom-content-text {
        text-align: center;
        width: 100%;
    }
    
    .custom-title {
        display: inline-block;
        text-decoration: none;
        padding: 0.5em 1em;
        text-align: center;
        width: 60%;
        font-size: 30px;
        font-family: "Roboto";
        font-weight: bold;
    }
    
    .custom-button:hover {
        background-color: #ffffff;
        text-decoration: none;
    }
    
    .custom-content-logo{
        width: 100%;
        text-align: center;
    }
    
    .custom-image{
        width: 300px;
    }
    
    .custom-image-sidebar {
        width: 200px;
    }
    
    .stButton>button {
        display: inline-block;
        padding: 0.5em 1em;
        color: #1722FF !important;
        border-radius: 10px;
        background-color: #FFD117;
        text-align: center;
        cursor: pointer;
        text-decoration: none;
        width: 100%;
        font-size: 15px;
        font-family: "Roboto";
        transition-duration: 0.2s;
        border-width: 2px 2px 2px 2px;
        border-style: solid;
        border-color: #FFD117;
        margin-top: 5%;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #ffffff;
        text-decoration: none;
        border-width: 2px 2px 2px 2px;
        border-style: solid;
        border-color: #FFD117;
    }
    
    .stButton>button:focus {
        text-decoration: none;
        border-width: 2px 2px 2px 2px;
        border-style: solid;
        border-color: #FFD117 !important;
    }
    
    .stTooltipHoverTarget>button {
        background-color: transparent;
        cursor: pointer;
        font-size: 10px;
        font-family: "Roboto";
        transition-duration: 0.2s;
        border: none !important;
        text-align: left;
        justify-content: left;
    }
    
    .stTooltipHoverTarget>button:hover {
        background-color: #FFFFFFF !important;
        text-decoration: none;
        border-width: 1px 1px 1px 1px !important;
        border-style: solid !important;
        border-color: #FFD117 !important;
        color: #000000 !important;
    }
    
    .stTooltipHoverTarget>button:focus {
        background-color: #FFFFFFF !important;
        text-decoration: none;
        border-width: 1px 1px 1px 1px !important;
        border-style: solid !important;
        border-color: #FFD117 !important;
        color: #000000 !important;
    }
    
    .stTooltipHoverTarget>button:active {
        background-color: #FFFFFFF !important;
        text-decoration: none;
        border-width: 1px 1px 1px 1px !important;
        border-style: solid !important;
        border-color: #FFD117 !important;
        color: #000000 !important;
    }
    
    .custom-content-name{
        font-size: 3.5rem;
        font-weight: 400;
        line-height: 4rem;
        font-family: Google Sans, Helvetica Neue, sans-serif;
        letter-spacing: normal;
        font-weight: 500;
        letter-spacing: -.03em;
        margin-top: 18px;
    }
    
    .custom-content-dude{
        font-size: 3rem;
        font-weight: 400;
        line-height: 4rem;
        font-family: Google Sans, Helvetica Neue, sans-serif;
        letter-spacing: normal;
        font-weight: 500;
        letter-spacing: -.03em;
        margin-top: -0.5em;
    }
    
    .custom-content-name span {
        position: relative;
        display: inline-block;
        background: -webkit-linear-gradient(74deg, #1722FF 0, #1722FF 9%, #FFD117 20%, #FFD117 24%, #1722FF 35%, #FFD117 44%, #1722FF 50%, #FFD117 56%, #131314 75%, #131314 100%);
        background: linear-gradient(74deg, #1722FF 0, #1722FF 9%, #FFD117 20%, #FFD117 24%, #1722FF 35%, #FFD117 44%, #1722FF 50%, #FFD117 56%, #131314 75%, #131314 100%);
        background-size: 400% 100%;
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .custom-content-dude span {
        position: relative;
        display: inline-block;
        color: #adafae;
        background-size: 400% 100%;
        background-clip: text;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

# Configuración de la aplicación
# st.title("💙 Dom-IA 💙")

# Configuración de OAuth2
CLIENT_SECRETS_FILE = "./client_secret.json"
SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]
REDIRECT_URI = 'http://localhost:8501/'
# REDIRECT_URI = 'https://dom-ia-r7zv7y2o5a-uc.a.run.app/' 
project_id = "domina-ia"

def save_credentials_to_cache(credentials):
    with open("credentials_cache.json", "w") as cache_file:
        cache_file.write(credentials.to_json())

def load_credentials_from_cache():
    if os.path.exists("credentials_cache.json"):
        with open("credentials_cache.json", "r") as cache_file:
            creds_data = json.load(cache_file)
            return Credentials.from_authorized_user_info(creds_data, SCOPES)
    return None

def authenticate_user():
    try:
        creds = load_credentials_from_cache()
        if not creds or not creds.valid:
            # del st.session_state['auth_url']
            flow = Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            query_params = st.query_params
            code = query_params.get("code")

            if code:
                flow.fetch_token(code=code)
                creds = flow.credentials
                save_credentials_to_cache(creds)
                st.session_state.credentials = creds
                st.query_params.clear()
                
                if creds and creds.token:
                    user_info = get_user_info(creds)
                    if user_info:
                        st.session_state.user_info = user_info
                    else:
                        st.error("No se pudo obtener la información del usuario.")
                else:
                    st.error("No se pudo obtener un token de acceso válido.")
            else:
                st.session_state.auth_url = auth_url
        else:
            if creds and creds.token:
                user_info = get_user_info(creds)
                if user_info:
                    st.session_state.user_info = user_info
                else:
                    st.error("No se pudo obtener la información del usuario.")
            else:
                st.error("No se pudo obtener un token de acceso válido.")
            st.session_state.credentials = creds

    except Exception as e:
        st.error(f'Error en la autenticación: {e}')

def get_user_info(creds):
    try:
        service = build('oauth2', 'v2', credentials=creds)
        user_info = service.userinfo().get().execute()
        return user_info
    except Exception as e:
        st.error(f'Error obteniendo la información del usuario: {e}')
        return None

@st.dialog("Nuevo Chat")
def createChat():
    new_chat_name = st.text_input("Nombre del Chat")
    if st.button("Crear Chat"):
        if new_chat_name:
            char_count = len(new_chat_name)
            
            if char_count <= 40:
                st.session_state.chats[new_chat_name] = []
                st.session_state.active_chat = new_chat_name
                createChatVertex(False)
                st.rerun()
            else:
                st.error("Por favor, ingresa un nombre mas corto.")
        else:
            st.error("Por favor, ingresa un nombre para el chat.")

def createChatVertex(context):
    if "credentials" not in st.session_state:
        st.error("No estás autenticado. Por favor, autentícate primero.")
        return

    creds = st.session_state.credentials
    vertexai.init(project=project_id, location="us-central1", credentials=creds)
    model = GenerativeModel(
        "gemini-1.5-flash-001",
        system_instruction=[
            "Eres un agente de Domina Entrega Total, llamado Dom-IA y siempre en tu primer interacción te presentaras como agente de productividad de Domina y tu nombre. No lo diras más si ya lo hiciste en la conversación",
            "debes dar respuestas concretas y enfocadas en un mundo corporativo y guiando al usuario siempre en alcanzar mejor productividad en tus tareas diarias.",
            "principalmente estarás recibiendo correos electrónicos para resumir y responder. También tendrás el reto de ayudar a las personas a acceder a conocimientos generales de forma mas rápida y sencilla",
            "cuando recibas documentos, audios o fotos inicia presentandote y da una respuesta donde primero tenga un resumen general con las conclusiones mas importantes",
            "en ocasiones, interactuarás con desarrolladores que te harán preguntas a nivel de código. Siempre prioriza las mejores prácticas y utiliza tecnologías actualizadas en el mercado para brindar respuestas precisas y efectivas."
        ],
    )
    if context is False:
        st.session_state.chatVertex = model.start_chat()
    else: 
        history = st.session_state.chatsContext.get(st.session_state.active_chat, [])
        st.session_state.chatVertex = model.start_chat(
            history=history, 
            response_validation=True
        )

def generate_response(prompt):
    try:
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
        
        chat = st.session_state.chatVertex

        response = chat.send_message(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # st.sidebar.success(model.count_tokens(prompt))

        return response.text

    except Exception as e:
        st.error(f"Error al obtener la respuesta: {e}")
        return "No se pudo obtener una respuesta en este momento."

authenticate_user()

# Inicializar el estado de la sesión para chats si no existe
if "chats" not in st.session_state:
    st.session_state.chats = {}
    
# Inicializar el estado de la sesión para el contexto de los chats si no existe
if "chatsContext" not in st.session_state:
    st.session_state.chatsContext = {}

# Botón de autenticación fijado al final del sidebar
if "auth_url" in st.session_state:
    st.markdown('<div class="custom-content-logo"><img class="custom-image" src="https://i.ibb.co/wgZcFLF/Domina-entrega-total.png"></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="custom-content-text"><p class="custom-title">Te damos la bienvenida a 💙 Dom-IA 💙</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-content-buttom"><a href="' + st.session_state.auth_url + '" class="custom-button">Iniciar Sesión</a></div>', unsafe_allow_html=True)

# Mostrar mensajes del chat activo
if "credentials" in st.session_state:
    
    # Crear un nuevo chat
    with st.sidebar:
        st.markdown('<div class="custom-content-logo"><img class="custom-image-sidebar" src="https://i.ibb.co/KGCFj7N/DOMIA.png"></div>', unsafe_allow_html=True)
        if st.button("Nuevo chat"):
            createChat()

    # Listar los chats creados en la barra lateral con scroll
    with st.sidebar:
        for chat_name in st.session_state.chats.keys():
            if st.button(chat_name, key=chat_name, help='Click para abrir el chat', use_container_width=True):
                st.session_state.active_chat = chat_name
                createChatVertex(True)

    
    if "active_chat" in st.session_state:
        active_chat = st.session_state.active_chat
        st.markdown('<h1 class="custom-content-name"><span>' + active_chat + '</span></h1>', unsafe_allow_html=True)

        # Mostrar historial de mensajes
        for message in st.session_state.chats[active_chat]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input para enviar mensajes en el chat activo
        if (prompt := st.chat_input("¿Qué dudas tienes?")):
            if active_chat not in st.session_state.chatsContext:
                st.session_state.chatsContext[active_chat] = []
            
            st.session_state.chats[active_chat].append({"role": "user", "content": prompt})
            st.session_state.chatsContext[active_chat].append(Content(role="user", parts=[Part.from_text(prompt)]))
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = generate_response(prompt)
                st.markdown("💙 Dom-IA 💙")
                st.markdown(response)
                st.session_state.chats[active_chat].append({"role": "assistant", "content": response})
                st.session_state.chatsContext[active_chat].append(Content(role="assistant", parts=[Part.from_text(response)]))
            
            # print(st.session_state.chats[active_chat])
            # print(st.session_state.chatsContext[active_chat])
    else:
        st.markdown('<h1 class="custom-content-name"><span> Hola, ' + st.session_state.user_info['given_name'] + '</span></h1>', unsafe_allow_html=True)
        st.markdown('<h1 class="custom-content-dude"><span> ¿En que puedo ayudarte? </span></h1>', unsafe_allow_html=True)
        st.warning("Por favor, selecciona o crea un chat para continuar.", icon="⚠")
