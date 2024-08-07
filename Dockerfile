FROM python:3


COPY requirements.txt /

RUN pip3 install -r requirements.txt

COPY ./app /app

COPY /docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
EXPOSE 3000

WORKDIR /app

CMD ["/docker-entrypoint.sh"]