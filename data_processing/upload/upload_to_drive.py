import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'data_processing/upload/credentials2.json', 
                ['https://www.googleapis.com/auth/drive.file'])
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def create_folder(folder_name, parent_folder_id=None):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    # Verifica se a pasta já existe
    if parent_folder_id:
        query = f"name='{folder_name}' and '{parent_folder_id}' in parents and trashed=false"
    else:
        query = f"name='{folder_name}' and trashed=false"
    
    existing_folders = service.files().list(q=query, fields='files(id)').execute()
    if existing_folders.get('files'):
        print(f"A pasta '{folder_name}' já existe no Google Drive.")
        return existing_folders['files'][0]['id']
    else:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]
        new_folder = service.files().create(body=folder_metadata, fields='id').execute()
        print(f"A pasta '{folder_name}' foi criada com sucesso no Google Drive.")
        return new_folder.get('id')

def upload_files_to_drive(local_folder_path, drive_parent_folder_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    # Dicionário para mapear as pastas locais às pastas no Google Drive
    drive_folder_map = {local_folder_path: drive_parent_folder_id}
    
    for root, dirs, files in os.walk(local_folder_path):
        # Verifica se o diretório atual já tem uma pasta correspondente no Google Drive
        parent_folder_id = drive_folder_map[root]
        
        for dir_name in dirs:
            local_subfolder_path = os.path.join(root, dir_name)
            # Cria a subpasta no Google Drive
            drive_subfolder_id = create_folder(dir_name, parent_folder_id)
            # Armazena o mapeamento da subpasta local para o ID da pasta no Drive
            drive_folder_map[local_subfolder_path] = drive_subfolder_id
        
        for file in files:
            file_path = os.path.join(root, file)
            file_metadata = {'name': file, 'parents': [parent_folder_id]}
            media = MediaFileUpload(file_path, resumable=True)
            uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f'File {file_path} uploaded with ID: {uploaded_file.get("id")}')

if __name__ == "__main__":
    # Nome da pasta raiz no Google Drive
    drive_root_folder_name = "Backup_ZareaDeRisco"
    local_folder = r"downloads/"
    
    # Cria a pasta raiz no Google Drive
    drive_root_folder_id = create_folder(drive_root_folder_name)
    
    # Faz o upload dos arquivos para o Google Drive
    upload_files_to_drive(local_folder, drive_root_folder_id)
