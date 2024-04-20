# Usa la imagen base oficial de Python
FROM python:3.10

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requerimientos al contenedor
COPY requirements.txt .
COPY serviceAccountKey.json .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install firebase-admin

# Copia el código actual al contenedor en el directorio /app
COPY . .

# Ejecuta la aplicación cuando el contenedor se inicie
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
