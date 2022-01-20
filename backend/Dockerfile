FROM python:3.9-slim-buster

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN apt-get update \
    && apt-get -y install netcat gcc postgresql libpq-dev \
    && apt-get clean

RUN pip install --upgrade pip
COPY . /backend
RUN pip install -r requirements.txt
