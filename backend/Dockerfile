#imagen a descargar
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN  pip install --upgrade pip --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONUNBUFFERED=1

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]