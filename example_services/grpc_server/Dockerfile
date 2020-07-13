FROM python:3.8-slim-buster

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app.py .
ADD app_pb2.py .
ADD app_pb2_grpc.py .

EXPOSE 50051

ENTRYPOINT ["python", "-u", "/app/app.py"]
