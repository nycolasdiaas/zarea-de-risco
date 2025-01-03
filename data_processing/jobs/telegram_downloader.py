import os
import asyncio
import json
import time
from datetime import datetime, timedelta
from telethon import TelegramClient
from dotenv import load_dotenv

from download.base_downloader import BaseTelegramDownloader
from download.compression import compress_with_ffmpeg, compress_with_zstd
from download.tar_utils import create_tar_from_zstd_files

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "None")
BASE_OUTPUT_FOLDER = os.getenv('BASE_OUTPUT_FOLDER', './downloads')
DAYS_OFFSET = int(os.getenv("DAYS_OFFSET", 0))
TIMEZONE_OFFSET = 3  # Fuso horário em horas
SESSION_NAME = os.getenv("SESSION_NAME", "session_name")

class TelegramDownloader(BaseTelegramDownloader):
    """
    Classe que herda de BaseTelegramDownloader e implementa a lógica de:
      - Agrupar mensagens com grouped_id
      - Baixar mídias chamando super().save_media(...)
      - Guardar as mídias como lista em metadata.json
    """

    def __init__(self, chats, max_workers=30, offset_days=None):
        """
        :param chats: lista de chats/canais que queremos processar
        :param max_workers: número de workers (herdado)
        :param offset_days: se não for None, define quantos dias atrás usar de offset
        """
        super().__init__(chats, max_workers=max_workers)
        self.offset_days = offset_days if offset_days is not None else DAYS_OFFSET

    async def start(self):
        """
        Conecta ao Telegram e processa as mensagens a partir do offset calculado.
        """
        total_start_time = time.time()

        async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
            # Calcula a data de offset
            # self.fuso_correto vem da classe base (datetime.now() - timedelta(hours=3))
            if self.offset_days > 0:
                offset_date = self.fuso_correto - timedelta(days=self.offset_days)
            else:
                offset_date = self.fuso_correto  # Se offset_days=0, pega "hoje" 

            for chat in self.chats:
                print(f"Processando mensagens a partir de {offset_date} para o chat: {chat}")
                await self.process_chat(client, chat, offset_date)

        total_elapsed_time = time.time() - total_start_time
        print(f"Tempo total de execução: {total_elapsed_time:.2f} segundos")