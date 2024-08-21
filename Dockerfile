# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requisitos y el código fuente al contenedor
COPY requirements.txt requirements.txt
COPY . .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto que Streamlit usará
EXPOSE 8501

# Ejecuta la aplicación de Streamlit
CMD ["streamlit", "run", "app.py"]
