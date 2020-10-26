FROM python:3.8-buster

WORKDIR /app

RUN apt-get update
RUN apt-get install -y libpq-dev python3-dev

COPY cicada2/runners/sql_runner/requirements.txt cicada2/runners/sql_runner/requirements.txt
RUN pip install -r cicada2/runners/sql_runner/requirements.txt

ADD cicada2/protos cicada2/protos
ADD cicada2/runners/sql_runner cicada2/runners/sql_runner
ADD cicada2/shared cicada2/shared

ADD cicada2/__init__.py cicada2/__init__.py
ADD cicada2/runners/__init__.py cicada2/runners/__init__.py

EXPOSE 50051
ENV PYTHONPATH :/app/cicada2

ENTRYPOINT [ "python", "-u", "cicada2/runners/sql_runner/main.py" ]
