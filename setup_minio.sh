#!/bin/bash

source .env

docker run -d -p 9000:9000 -p 9090:9090 --name minio \
  -v /mnt/wsl/minio/data:/data \
  -v /mnt/wsl/minio/config:/root/.minio \
  minio/minio server /data --console-address ":9090"
