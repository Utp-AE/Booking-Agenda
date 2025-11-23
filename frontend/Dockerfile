#imagen a descargar

#frontend
FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html
COPY register.html /usr/share/nginx/html/register.html

#FROM ubuntu:24.04

#instalacion de Python
#RUN 	apt update && apt upgrade -y && \
#	apt install nano supervisor -y && \
#	apt install build-essential libssl-dev libffi-dev python3-pip python3-dev python3-venv -y && \
#	apt install python3-cffi python3-brotli -y && \
#	apt install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 -y
 
#crear el entorno virtual de python
#RUN	mkdir -p /opt/demo_api/workspace/envs && \
#	python3 -m venv /opt/demo_api/workspace/envs/demo_api

#activar el entorno
#RUN	 . /opt/demo_api/workspace/envs/demo_api/bin/activate

#Exponer puerto
#EXPOSE 80

#CMD ["/bin/bash", "-c", "/usr/bin/supervisord && supervisorctl reread && supervisorctl update && tail -f /dev/null"]