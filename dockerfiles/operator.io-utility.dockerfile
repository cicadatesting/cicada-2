FROM python:3.8-buster

WORKDIR /app

COPY cicada2/operator/io_utility/requirements.txt cicada2/operator/io_utility/requirements.txt
RUN pip install -r cicada2/operator/io_utility/requirements.txt

ADD cicada2/operator/io_utility cicada2/operator/io_utility

ADD cicada2/__init__.py cicada2/__init__.py

ENV PYTHONPATH :/app/cicada2

ENTRYPOINT [ "python", "-u", "cicada2/operator/io_utility/app.py" ]