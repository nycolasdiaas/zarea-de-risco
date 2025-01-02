import os
import asyncio
import json
import time
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from download.base_downloader import BaseTelegramDownloader
from download.compression import compress_with_ffmpeg, compress_with_zstd
from download.tar_utils import create_tar_from_zstd_files
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "None")
BASE_OUTPUT_FOLDER = os.getenv('BASE_OUTPUT_FOLDER', './downloads')
DAYS_OFFSET = int(os.getenv("DAYS_OFFSET", 0))
MIN_DATE = os.getenv("MIN_DATE", None)
MAX_DATE = os.getenv("MAX_DATE", None)
TIMEZONE_OFFSET = 3  # Fuso horário em horas
SESSION_NAME = os.getenv("SESSION_NAME", "session_name")


class TelegramDownloader(BaseTelegramDownloader):
    async def save_media(self, message, media_folder, chat_name):
        """
        Baixa, recomprime (se necessário) e compacta arquivos de mídia.
        """
        # Ajusta a data da mensagem para incluir o fuso horário
        message_date = (message.date + timedelta(hours=TIMEZONE_OFFSET)).strftime("%Y-%m-%d")

        base_folder = os.path.join(media_folder, chat_name,"past_dates", message_date)
        media_folder = os.path.join(base_folder, "media")
        os.makedirs(media_folder, exist_ok=True)

        # Caminho para o arquivo metadata.json
        metadata_path = os.path.join(base_folder, "metadata.json")

        # Carregar metadados existentes, se houver
        existing_metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as meta_file:
                existing_metadata = json.load(meta_file)

        # Verificar se a mídia já foi processada
        media_id = str(message.id)
        if media_id in existing_metadata:
            print(f"Mídia com ID {media_id} já existe no metadata.json. Ignorando download.")
            return None, None

        # Salva o arquivo no diretório correto
        file_path, media_type = await super().save_media(message, media_folder)

        # Atualizar metadados com a nova mídia
        data = {
                    "id": message.id,
                    "peer_id": {
                        "type": "PeerChannel",
                        "channel_id": (
                            message.peer_id.channel_id
                            if hasattr(message.peer_id, "channel_id")
                            else None
                        ),
                    },
                    "date": (message.date - timedelta(hours=3)).isoformat(),
                    "message": message.text,
                    "reply_to": {
                        "reply_to_msg_id": (
                            message.reply_to.reply_to_msg_id
                            if message.reply_to
                            else None
                        )
                    },
                    "flags": {
                        "out": message.out,
                        "mentioned": message.mentioned,
                        "media_unread": message.media_unread,
                        "silent": message.silent,
                        "post": message.post,
                        "from_scheduled": message.from_scheduled,
                        "legacy": message.legacy,
                        "edit_hide": message.edit_hide,
                        "pinned": message.pinned,
                        "noforwards": message.noforwards,
                        "invert_media": message.invert_media,
                        "offline": message.offline,
                        "video_processing_pending": message.video_processing_pending,
                    },
                    "from_id": message.sender_id,
                    "media": (
                        {
                            "type": "MessageMediaPhoto" if message.media else None,
                            "photo": (
                                {
                                    "id": (
                                        message.media.photo.id
                                        if message.media
                                        and hasattr(message.media, "photo")
                                        else None
                                    ),
                                    "access_hash": (
                                        message.media.photo.access_hash
                                        if message.media
                                        and hasattr(message.media, "photo")
                                        else None
                                    ),
                                    "file_reference": None,
                                    "date": (
                                        (message.media.photo.date - timedelta(hours=3)).isoformat()
                                        if message.media
                                        and hasattr(message.media, "photo")
                                        else None
                                    ),
                                    "sizes": None,
                                    "dc_id": None,
                                    "has_stickers": None,
                                    "video_sizes": None,
                                }
                                if message.media
                                else None
                            ),
                            "ttl_seconds": None,
                        }
                        if message.media
                        else None
                    ),
                    "media_path": file_path if file_path else None,
                    "views": message.views,
                    "forwards": message.forwards,
                    "replies": (
                        {
                            "replies": (
                                message.replies.replies if message.replies else None
                            ),
                            "replies_pts": (
                                message.replies.replies_pts if message.replies else None
                            ),
                            "comments": (
                                message.replies.comments if message.replies else None
                            ),
                            "recent_repliers": [],
                            "channel_id": (
                                message.replies.channel_id if message.replies else None
                            ),
                            "max_id": None,
                            "read_max_id": None,
                        }
                        if message.replies
                        else None
                    ),
                    "edit_date": (
                        (message.edit_date - timedelta(hours=3)).isoformat() if message.edit_date else None
                    ),
                    "reactions": (
                        [
                            {
                                "reaction": reaction.reaction.emoticon,
                                "count": reaction.count,
                            }
                            for reaction in message.reactions.results
                        ]
                        if message.reactions
                        else []
                    ),
                }
        
        # existing_metadata[media_id] = data
        # Verifica se os metadados já existem como uma lista
        if isinstance(existing_metadata, dict):
            # Se estiver no formato antigo (dicionário), converte para lista
            existing_metadata = list(existing_metadata.values())

        # Adiciona o novo registro à lista
        existing_metadata.append(data)

        # Salvar metadados atualizados no arquivo metadata.json
        with open(metadata_path, "w", encoding="utf-8") as meta_file:
            json.dump(existing_metadata, meta_file, ensure_ascii=False, indent=4)
            

        if not file_path or media_type != "video":
            return file_path, media_type

        recompressed_file_path = file_path.replace(".mp4", "_recompressed.mp4")
        compressed_file_path = f"{recompressed_file_path}.zstd"

        loop = asyncio.get_event_loop()
        start_recompressed_file = time.time()
        # recompressed_file_path = await loop.run_in_executor(
        #     None, compress_with_ffmpeg, file_path, recompressed_file_path
        # )
        # total_recompressed_time = time.time() - start_recompressed_file
        # print(f"Tempo total de recompilação dos vídeos: {total_recompressed_time:.2f} segundos")
        # compressed_file_path = await loop.run_in_executor(
        #     None, compress_with_zstd, recompressed_file_path, compressed_file_path
        # )

        return file_path, media_type

    async def post_process_chat(self, chat_folder):
        """
        Cria arquivos TAR.ZSTD para cada pasta de mídia processada.
        """
        for root, dirs, _ in os.walk(chat_folder):
            for folder in dirs:
                media_folder = os.path.join(root, folder, "media")
                if os.path.exists(media_folder):
                    print(f"Agrupando arquivos em TAR.ZSTD para a pasta: {media_folder}")
                    await asyncio.get_event_loop().run_in_executor(
                        None, create_tar_from_zstd_files, media_folder
                    )

    async def start(self):
        """
        Processa mensagens com base no intervalo de datas configurado.
        """
        total_start_time = time.time()
        async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
            # Calcular o intervalo de datas
            offset_date = self.calculate_offset_date()

            for chat in self.chats:
                print(f"Processando mensagens para o chat: {chat}\nDe {offset_date}")
                await self.process_chat(client, chat, offset_date)

        total_elapsed_time = time.time() - total_start_time  # Tempo total decorrido
        print(f"Tempo total de execução: {total_elapsed_time:.2f} segundos")

    def calculate_offset_date(self):
        """
        Calcula a data mínima (offset_date) com base no DAYS_OFFSET.
        """
        # Calcula a data mínima como DAYS_OFFSET dias atrás
        tz_offset = timedelta(hours=TIMEZONE_OFFSET)
        offset_date = datetime.now() - timedelta(days=DAYS_OFFSET)
        offset_date = offset_date.replace(hour=0, minute=0, second=0, microsecond=0) + tz_offset
        return offset_date



    async def process_chat(self, client, chat, offset_date):
        """
        Processa mensagens de um chat dentro de um intervalo de datas.
        """
        async for message in client.iter_messages(chat, offset_date=offset_date, reverse=True):
            # Ajusta o timezone da mensagem para offset-naive
            message_date_adjusted = (message.date - timedelta(hours=TIMEZONE_OFFSET)).replace(tzinfo=None)

            # # Verifica se a mensagem está fora do intervalo inferior
            # if message_date_adjusted < offset_date.replace(tzinfo=None):
            #     print(f"Mensagem antes do intervalo ({message_date_adjusted}), ignorada.")
            #     continue

            # Processa a mensagem, recriando o diretório com base no nome do chat e na data ajustada
            await self.save_media(message, BASE_OUTPUT_FOLDER, chat)
            print(f"Mensagem processada: {message_date_adjusted}")
