# Usamos una imagen base oficial de Python ligera
FROM python :3.11-slim

# Evitamos que Python escriba archivos . pyc y buffer de logs
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los requerimientos e instalamos dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del codigo fuente
COPY . /app/

# Comando por defecto al iniciar el contenedor
CMD [" python " , " manage . py " , " runserver " , "0.0.0.0:8000"]