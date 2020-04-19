FROM python:3.8-buster

WORKDIR /app

COPY cicada2/engine/requirements.txt cicada2/engine/requirements.txt
RUN pip install -r cicada2/engine/requirements.txt

ADD cicada2/protos cicada2/protos
ADD cicada2/engine cicada2/engine
ADD cicada2/shared cicada2/shared

ADD cicada2/__init__.py cicada2/__init__.py

ENV PYTHONPATH :/app/cicada2

ENTRYPOINT [ "python", "cicada2/engine/main.py" ]
