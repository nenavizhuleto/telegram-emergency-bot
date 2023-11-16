FROM python:3.11-slim

RUN apt update && apt install gcc -y

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/

RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT [ "bash", "docker-entrypoint.sh" ]
