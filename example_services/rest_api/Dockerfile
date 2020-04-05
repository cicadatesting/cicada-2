FROM python:3.8-buster

WORKDIR /app

RUN apt-get update
RUN apt-get install -y libpq-dev python-dev

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app.py .

ENTRYPOINT ["python", "app.py"]
