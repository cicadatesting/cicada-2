FROM python:3.8-buster

WORKDIR /app

RUN apt-get update
RUN apt-get install -y libpq-dev python-dev

# TODO: Render a handlebars template for runners on runner build
# or have seperate requirements.txt per project
ADD requirements.txt .
RUN pip install -r requirements.txt

ADD cicada2/protos cicada2/protos
ADD cicada2/runners/RESTRunner cicada2/runners/RESTRunner
ADD cicada2/runners/util cicada2/runners/util

ADD cicada2/__init__.py cicada2/__init__.py
ADD cicada2/runners/__init__.py cicada2/runners/__init__.py

EXPOSE 50051
ENV PYTHONPATH :/app/cicada2

ENTRYPOINT [ "python", "cicada2/runners/RESTRunner/main.py" ]
