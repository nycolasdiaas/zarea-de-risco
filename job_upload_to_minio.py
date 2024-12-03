import os
from minio import Minio
from minio.error import S3Error

minio_client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"), 
    secret_key=os.getenv("MINIO_SECRECT_KEY"), 
    secure=False 
)


bucket_name = os.getenv("MINIO_BUCKET_NAME")
base_output_folder = "./downloads/"


def upload_to_minio(file_path, file_name, remote_folder):
    try:
        if not minio_client.bucket_exists(bucket_name):
            print(f"Bucket '{bucket_name}' não existe. Criando...")
            minio_client.make_bucket(bucket_name)

        remote_path = os.path.join(remote_folder, file_name).replace(os.sep, '/')

        # upload
        minio_client.fput_object(bucket_name, remote_path, file_path)
        print(f"Arquivo '{file_name}' enviado para o MinIO em '{remote_path}'.")
        os.remove(file_path)
        print(f"Arquivo '{file_name}' removido localmente após o upload.")

    except S3Error as e:
        print(f"Erro ao enviar para o MinIO: {e}")

def upload_folder_to_minio(local_folder, remote_folder):
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, local_folder)
            upload_to_minio(local_file_path, relative_path, remote_folder)

os.makedirs(base_output_folder, exist_ok=True)


try:
    print(f"Access Key: {os.getenv('MINIO_ACCESS_KEY')}")
    print(f"Secret Key: {os.getenv('MINIO_SECRECT_KEY')}")
    for chat in os.listdir(base_output_folder):
        group_folder = os.path.join(base_output_folder, chat)
        if os.path.isdir(group_folder):
            for current_date in os.listdir(group_folder):
                date_folder = os.path.join(group_folder, current_date)
                if os.path.isdir(date_folder):
                    remote_folder = f'{chat}/{current_date}'
                    upload_folder_to_minio(date_folder, remote_folder)

except Exception as e:
    print(f"Erro ao subir os arquivos para o MinIO: {e}")
