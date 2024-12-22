import os
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
from concurrent.futures import ProcessPoolExecutor
from download.compression import compress_with_ffmpeg, compress_with_zstd
from download.tar_utils import create_tar_from_zstd_files
from dotenv import load_dotenv
import json

load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "None")
BASE_OUTPUT_FOLDER = "./downloads"
DAYS_OFFSET = int(os.getenv("DAYS_OFFSET"), 0)

class TelegramDownloader:
    def __init__(self, chats, max_workers=10, compression_workers=4):
        self.chats = chats
        self.max_workers = max_workers
        self.compression_workers = compression_workers
        self.fuso_correto = datetime.utcnow() - timedelta(hours=3)
        self.queue = asyncio.Queue()
        self.executor = ProcessPoolExecutor(max_workers=self.compression_workers)

    async def retry_download(self, message, file_path, retries=3, delay=2):
        """
        Realiza múltiplas tentativas de download.
        """
        for attempt in range(retries):
            try:
                print(f"Tentativa {attempt + 1} para baixar: {file_path}")
                result = await message.download_media(file=file_path)
                if result and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    return True
            except Exception as e:
                print(f"Erro no download: {e}")
            await asyncio.sleep(delay)
        return False

    async def save_media(self, message, media_folder):
        """
        Baixa, recomprime (se necessário) e compacta arquivos de mídia.
        """
        if not message.media:
            print(f"Mensagem ID {message.id} não contém mídia.")
            return None, None

        media_type = None
        file_name = None
        if hasattr(message.media, "photo"):
            media_type = "photo"
            file_name = f"photo_{message.id}.jpg"
        elif hasattr(message.media, "video"):
            media_type = "video"
            file_name = f"video_{message.id}.mp4"
        elif hasattr(message.media, "document"):
            if hasattr(message.media.document, "mime_type") and message.media.document.mime_type.startswith("audio/"):
                media_type = "audio"
                file_name = f"audio_{message.id}.mp3"
            elif hasattr(message.media.document, "attributes"):
                for attr in message.media.document.attributes:
                    if isinstance(attr, type(message.media.document)):
                        media_type = "audio"
                        file_name = f"voice_{message.id}.ogg"
        elif hasattr(message.media, "audio"):
            media_type = "audio"
            file_name = f"audio_{message.id}.mp3"

        if not media_type or not file_name:
            return None, None

        original_file_path = os.path.join(media_folder, file_name)
        recompressed_file_path = os.path.join(media_folder, f"recompressed_{file_name}")
        compressed_file_path = f"{recompressed_file_path}.zstd"

        print(f"Baixando mídia: {original_file_path}")
        if not await self.retry_download(message, original_file_path):
            print(f"Erro ao baixar: {original_file_path}")
            return None, None

        loop = asyncio.get_event_loop()

        if media_type == "video":
            recompressed_file_path = await loop.run_in_executor(
                self.executor, compress_with_ffmpeg, original_file_path, recompressed_file_path
            )
            if not recompressed_file_path:
                return None, None
            original_file_path = recompressed_file_path

        compressed_file_path = await loop.run_in_executor(
            self.executor, compress_with_zstd, original_file_path, compressed_file_path
        )
        if not compressed_file_path:
            return None, None

        return compressed_file_path, media_type

    async def process_message(self, message, chat_folder):
        """
        Processa uma única mensagem.
        """
        message_date = (message.date - timedelta(hours=3)).date()
        media_folder = os.path.join(chat_folder, str(message_date), "media")
        os.makedirs(media_folder, exist_ok=True)

        media_path, media_type = await self.save_media(message, media_folder)

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
                    "media_path": media_path if media_path else None,
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
        return message_date, data

    async def worker(self, chat_folder):
        """
        Processa mensagens da fila.
        """
        while True:
            message = await self.queue.get()
            if message is None:
                break
            try:
                message_date, data = await self.process_message(message, chat_folder)
                output_file = os.path.join(chat_folder, str(message_date), "metadata.json")
                os.makedirs(os.path.dirname(output_file), exist_ok=True)

                async with asyncio.Lock():
                    if os.path.exists(output_file):
                        with open(output_file, "r", encoding="utf-8") as f:
                            messages = json.load(f)
                    else:
                        messages = []

                    messages.append(data)
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(messages, f, ensure_ascii=False, indent=4)

            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
            finally:
                self.queue.task_done()

    async def group_media_by_date(self, chat_folder):
        for root, dirs, _ in os.walk(chat_folder):
            for folder in dirs:
                media_folder = os.path.join(root, folder, "media")
                if os.path.exists(media_folder):
                    await asyncio.get_event_loop().run_in_executor(
                        self.executor, create_tar_from_zstd_files, media_folder
                    )

    async def process_chat(self, client, chat):
        """
        Processa mensagens de um chat.
        """
        chat_folder = os.path.join(BASE_OUTPUT_FOLDER, chat)
        os.makedirs(chat_folder, exist_ok=True)

        async for message in client.iter_messages(chat, offset_date=self.fuso_correto - timedelta(days=DAYS_OFFSET), reverse=True):
            await self.queue.put(message)

        workers = [asyncio.create_task(self.worker(chat_folder)) for _ in range(self.max_workers)]

        await self.queue.join()
        for _ in range(self.max_workers):
            await self.queue.put(None)
        await asyncio.gather(*workers)

        await self.group_media_by_date(chat_folder)

    async def start(self):
        """
        Ponto de entrada para o processamento.
        """
        async with TelegramClient("session_name", API_ID, API_HASH) as client:
            for chat in self.chats:
                print(f"Processando chat: {chat}")
                await self.process_chat(client, chat)
