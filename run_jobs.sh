#bin/bash

docker-compose up -d

docker start minio

.venv/bin/python3 job_download_data.py > logs/job_download_data.txt

# .venv/bin/python3 job_upload_to_minio.py > logs/job_upload_to_minio.txt