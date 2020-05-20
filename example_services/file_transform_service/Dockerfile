FROM python:3.8-slim-buster

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app.py .

ENTRYPOINT ["python", "-u", "app.py"]
