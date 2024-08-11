FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \ 
    python3.12 \
    python3-pip \
    ffmpeg \
    intel-media-va-driver-non-free



COPY requirements.txt /

RUN apt-get update && apt-get install -y \ 
    pkg-config libmariadb-dev
RUN pip install -r requirements.txt --break-system-packages
RUN apt-get install -y python-is-python3

COPY ./app /app

COPY /docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
EXPOSE 3000

WORKDIR /app

CMD ["/docker-entrypoint.sh"]