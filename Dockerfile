FROM python:3.14-slim

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install -r requirements.txt

ADD . /app/