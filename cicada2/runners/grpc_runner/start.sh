#!/bin/bash

# Compile protos in /incoming_protos to /app/incoming_protos directory
python -m grpc_tools.protoc -I / --python_out=. --grpc_python_out=. /incoming_protos/*.proto

python -u /app/cicada2/runners/grpc_runner/main.py
