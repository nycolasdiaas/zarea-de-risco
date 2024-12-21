from os import path, makedirs, getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
from tqdm import tqdm
from telethon.sync import TelegramClient
import zstandard as zstd

load_dotenv()

API_ID = int(getenv("TELEGRAM_API_ID", 0))
API_HASH = getenv("TELEGRAM_API_HASH", "None")
SESSION_NAME = getenv("SESSION_NAME")

chats = [getenv("TELEGRAM_CHATS")]
base_output_folder = "/home/nycolasdiaas/Projetos/zarea-de-risco/downloads"

# Função para salvar mídia
def save_media(message, media_folder):
    if not message.media:
        return None, None

    try:
        media_type = None
        file_name = None

        if isinstance(message.media, message.media.__class__):
            if hasattr(message.media, "photo"):
                media_type = "photo"
                file_name = f"photo_{message.id}.jpg"
            elif hasattr(message.media, "video"):
                media_type = "video"
                file_name = f"video_{message.id}.mp4"
            elif hasattr(message.media, "audio"):
                media_type = "audio"
                file_name = f"audio_{message.id}.mp3"
            elif hasattr(message.media, "document"):
                media_type = "document"
                file_name = f"document_{message.id}.pdf"
            elif hasattr(message.media, "animation"):
                media_type = "animation"
                file_name = f"animation_{message.id}.gif"
            elif hasattr(message.media, "voice"):
                media_type = "voice"
                file_name = f"voice_{message.id}.ogg"
            elif hasattr(message.media, "sticker"):
                media_type = "sticker"
                file_name = f"sticker_{message.id}.webp"

        if not media_type or not file_name:
            return None, None

        compressed_file_name = f"{file_name}.zstd"
        compressed_file_path = path.join(media_folder, compressed_file_name)

        if path.exists(compressed_file_path):
            print(f"A mídia já foi baixada e comprimida: {compressed_file_path}")
            relative_path = path.relpath(compressed_file_path, base_output_folder)
            return relative_path, media_type

        temp_path = path.join(media_folder, file_name)
        total_size = getattr(message.media, "size", None)

        if total_size:
            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=f"Baixando {file_name}",
            ) as pbar:
                message.download_media(
                    file=temp_path,
                    progress_callback=lambda d, t: pbar.update(d - pbar.n if t else 0),
                )
        else:
            message.download_media(file=temp_path)

        # Comprimir arquivo
        with open(compressed_file_path, "wb") as compressed_file:
            compressor = zstd.ZstdCompressor(level=3, threads=4)
            with open(temp_path, "rb") as temp_file:
                compressor.copy_stream(temp_file, compressed_file)

        print(f"Arquivo salvo: {compressed_file_path}")
        return path.relpath(compressed_file_path, base_output_folder), media_type

    except Exception as e:
        print(f"Erro ao salvar mídia: {e}")
        return None, None


# Função para buscar mensagens
def fetch_messages(client, chat, offset_days=0):
    offset_date = datetime.now() - timedelta(days=offset_days)
    return list(client.iter_messages(chat, offset_date=offset_date, reverse=True))


# Processar chats
def process_chats(client, chats):
    makedirs(base_output_folder, exist_ok=True)

    for chat in chats:
        group_folder = path.join(base_output_folder, chat)
        all_messages = fetch_messages(client, chat, offset_days=0)

        messages_by_date = {}
        with tqdm(
            total=len(all_messages),
            desc=f"Processando {chat}",
            unit="msg",
        ) as pbar:
            for message in all_messages:
                message_date = (message.date - timedelta(hours=3)).date()
                media_folder = path.join(group_folder, str(message_date), "media")
                makedirs(media_folder, exist_ok=True)

                media_path, media_type = save_media(message, media_folder)

                data = {
                    "id": message.id,
                    "date": (message.date - timedelta(hours=3)).isoformat(),
                    "message": message.text,
                    "media_path": media_path,
                    "media_type": media_type,
                }

                if message_date not in messages_by_date:
                    messages_by_date[message_date] = []
                messages_by_date[message_date].append(data)
                pbar.update(1)

        # Salvar mensagens por data
        for date, messages in messages_by_date.items():
            output_file = path.join(group_folder, str(date), "metadata.json")
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(messages, json_file, ensure_ascii=False, indent=4)
            print(f"Mensagens salvas em: {output_file}")


# Execução principal
with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
    process_chats(client, chats)
