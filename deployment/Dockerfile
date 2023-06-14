FROM python:3.8.10-buster

# Environment variables
ARG API_KEY
ENV API_KEY=$API_KEY

RUN apt-get update
RUN apt-get install -y software-properties-common

RUN apt-get install -y \
    python3-pip python3-dev python3-setuptools \
    --no-install-recommends

RUN apt-get update && apt-get install gettext nano vim -y

RUN pip3 install --upgrade pip
RUN apt-get install -y cron

WORKDIR /src
COPY . /src

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN echo "Asia/Bangkok" > /etc/timezone && rm /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

RUN python3 manage.py collectstatic

COPY deployment/entrypoint entrypoint
COPY deployment/start.sh start
COPY deployment/celery/worker_start start-celeryworker
COPY deployment/celery/beat_start start-celerybeat

RUN chmod +x entrypoint
RUN chmod +x start
RUN chmod +x start-celeryworker
RUN chmod +x start-celerybeat

CMD ./entrypoint