FROM python:3.8
MAINTAINER Vadim Kozyrevskii 'vadikko2@mail.ru'

RUN apt-get update -y

RUN apt-get install -y python3-setuptools

COPY requirements.txt requirements.txt

RUN python -m pip install -r requirements.txt

WORKDIR /slackbot
