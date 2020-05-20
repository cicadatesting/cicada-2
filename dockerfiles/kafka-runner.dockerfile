FROM python:3.8-slim-buster

WORKDIR /app

COPY cicada2/runners/kafka_runner/requirements.txt cicada2/runners/kafka_runner/requirements.txt
RUN pip install -r cicada2/runners/kafka_runner/requirements.txt

ADD cicada2/protos cicada2/protos
ADD cicada2/runners/kafka_runner cicada2/runners/kafka_runner
ADD cicada2/shared cicada2/shared

ADD cicada2/__init__.py cicada2/__init__.py
ADD cicada2/runners/__init__.py cicada2/runners/__init__.py

EXPOSE 50051
ENV PYTHONPATH :/app/cicada2

ENTRYPOINT [ "python", "-u", "cicada2/runners/kafka_runner/main.py" ]
