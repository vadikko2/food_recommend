FROM python:3.8
MAINTAINER Vadim Kozyrevskii 'vadikko2@mail.ru'

RUN apt-get update -y

RUN apt-get install -y python-setuptools

#RUN apt-get install python-pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /crawler
