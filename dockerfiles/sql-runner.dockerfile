FROM python:3.8-buster

WORKDIR /app

RUN apt-get update
RUN apt-get install -y libpq-dev python-dev

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD cicada2/protos cicada2/protos
ADD cicada2/runners/SQLRunner cicada2/runners/SQLRunner

ADD cicada2/__init__.py cicada2/__init__.py
ADD cicada2/runners/__init__.py cicada2/runners/__init__.py

EXPOSE 50051
ENV PYTHONPATH :/app/cicada2

ENTRYPOINT [ "python", "cicada2/runners/SQLRunner/main.py" ]
