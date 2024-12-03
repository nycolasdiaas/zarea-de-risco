from telethon.sync import TelegramClient
import pandas as pd
import datetime
import os
from tqdm import tqdm

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

chats = ['Portalnoticiasceara']
base_output_folder = "./downloads/"
df_list = []

def save_media(message, media_folder):
    if message.media:
        try:
            media_type = None
            file_name = None
            
            if isinstance(message.media, message.media.__class__):
                if hasattr(message.media, 'photo'):
                    media_type = "photo"
                    file_name = f"photo_{message.id}.jpg"
                elif hasattr(message.media, 'video'):
                    media_type = "video"
                    file_name = f"video_{message.id}.mp4"
                elif hasattr(message.media, 'audio'):
                    media_type = "audio"
                    file_name = f"audio_{message.id}.mp3"
                elif hasattr(message.media, 'document'):
                    media_type = "document"
                    file_name = f"document_{message.id}.pdf"
                elif hasattr(message.media, 'animation'):
                    media_type = "animation"
                    file_name = f"animation_{message.id}.gif"
                elif hasattr(message.media, 'voice'):
                    media_type = "voice"
                    file_name = f"voice_{message.id}.ogg"
                elif hasattr(message.media, 'sticker'):
                    media_type = "sticker"
                    file_name = f"sticker_{message.id}.webp"
            
            if media_type is None or file_name is None:
                return None, None

            file_path = os.path.join(media_folder, file_name)

            if os.path.exists(file_path):
                print(f"A mídia já foi baixada: {file_name}")
                return file_path, media_type

            total_size = message.media.size if hasattr(message.media, 'size') else None
            
            if total_size:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Baixando {file_name}") as pbar:
                    file_path = message.download_media(file=file_path, progress_callback=lambda d, t: pbar.update(d - pbar.n if t else 0))
            else:
                file_path = message.download_media(file=file_path)
            
            return file_path, media_type

        except Exception as e:
            print(f"Erro ao baixar mídia: {e}")
            return None, None
    return None, None

os.makedirs(base_output_folder, exist_ok=True)

for chat in chats:
    group_folder = os.path.join(base_output_folder, chat)
    os.makedirs(group_folder, exist_ok=True)
    
    current_date = datetime.date.today()
    date_folder = os.path.join(group_folder, str(current_date))
    os.makedirs(date_folder, exist_ok=True)
    
    media_folder = os.path.join(date_folder, 'media')
    os.makedirs(media_folder, exist_ok=True)

    with TelegramClient('session_name', api_id, api_hash) as client:
        all_messages = list(client.iter_messages(chat, offset_date=datetime.date.today(), reverse=True))
        
        with tqdm(total=len(all_messages), desc="Processando mensagens e baixando mídias", unit="msg", position=0, leave=True) as pbar:
            for message in all_messages:
                print(f"\nProcessando mensagem ID: {message.id}")
                
                media_path, media_type = save_media(message, media_folder)
                
                data = {
                    "group": chat,
                    "sender_id": message.sender_id,
                    "text": message.text,
                    "date": (message.date - datetime.timedelta(hours=3)),
                    "message_id": message.id,
                    "media_path": media_path,
                    "media_type": media_type,
                    "media_caption": message.media.caption if message.media and hasattr(message.media, 'caption') else None
                }
                
                df_list.append(data)
                pbar.update(1)

df = pd.DataFrame(df_list)
df['date'] = df['date'].dt.tz_localize(None)
output_file = os.path.join(date_folder, f"metadata_{current_date}.xlsx")
df.to_excel(output_file, index=False)
print(f"Dados salvos em {output_file}")
