FROM python:3.14-slim

RUN mkdir /app

WORKDIR /app

COPY requirements.txt constraints.txt /app/

RUN pip install --upgrade pip && pip install  -c constraints.txt -r requirements.txt

ADD . /app/