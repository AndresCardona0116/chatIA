import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
import json

st.title("💙 DOMICHAT con Vertex AI 💙")

# Configuración de OAuth2
CLIENT_SECRETS_FILE = ".\client_secret.json"  # Cambia esto a la ruta de tu archivo JSON

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

def authenticate_user():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES
    )
    creds = flow.run_local_server(port=8501)  # Asegúrate de que el puerto coincida con el que usas
    return creds.token

def generate_response(prompt, access_token):
    try:
        # Configuración de la solicitud HTTP
        url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/endpoints/gemini-1.5-flash-001:predict"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        data = {
            "instances": [{"content": prompt}],
            "parameters": {
                "max_output_tokens": 8192,
                "temperature": 1,
                "top_p": 0.95,
            },
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["predictions"][0]
        else:
            st.error(f"Error en la solicitud: {response.status_code}, {response.text}")
            return "No se pudo obtener una respuesta en este momento."
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

# Autenticación del usuario
if st.sidebar.button("Autenticar con Google"):
    access_token = authenticate_user()
    if access_token:
        st.session_state.access_token = access_token
        st.success("Autenticación exitosa. Ahora puedes hacer preguntas.")
    else:
        st.error("Error en la autenticación.")

if "access_token" in st.session_state:
    if (prompt := st.chat_input("¿Qué dudas tienes?")):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = generate_response(prompt, st.session_state.access_token)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.warning("Por favor, autentícate con Google para continuar.", icon="⚠")
