from python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app 

RUN pip install -r requirements.txt


COPY . /app

RUN python3 db_init.py

