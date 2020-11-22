FROM python:3.8-slim-buster

WORKDIR /app

COPY cicada2/verification/requirements.txt cicada2/verification/requirements.txt
RUN pip install -r cicada2/verification/requirements.txt

ADD cicada2/verification cicada2/verification
ADD cicada2/shared cicada2/shared
ADD cicada2/engine cicada2/engine

ADD cicada2/__init__.py cicada2/__init__.py

ENV PYTHONPATH :/app/cicada2

ENTRYPOINT [ "python", "-u", "cicada2/verification/app.py" ]