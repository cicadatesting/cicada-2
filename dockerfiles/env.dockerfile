FROM python:3.8-buster

WORKDIR /opt

RUN apt-get update
RUN apt-get install docker.io -y
RUN apt-get install -y libpq-dev python-dev

RUN pip install ipython

ADD requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH :/app/cicada2
