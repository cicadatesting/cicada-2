FROM python:3.8-buster

WORKDIR /app

COPY cicada2/operator/daemon/requirements.txt cicada2/operator/daemon/requirements.txt
RUN pip install -r cicada2/operator/daemon/requirements.txt

ADD cicada2/operator/daemon cicada2/operator/daemon

ADD cicada2/__init__.py cicada2/__init__.py

ENV PYTHONPATH :/app/cicada2

ENTRYPOINT [ "kopf", "run", "cicada2/operator/daemon/main.py", "--verbose" ]