from download.base_downloader import BaseTelegramDownloader
from telethon import TelegramClient
import os
import time
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "None")
BASE_OUTPUT_FOLDER = os.getenv('BASE_OUTPUT_FOLDER', './downloads')
DAYS_OFFSET = int(os.getenv("DAYS_OFFSET"), 0)
SESSION_NAME = os.getenv("SESSION_NAME", "session_name")

class TelegramDownloaderSimple(BaseTelegramDownloader):
    async def start(self):
        """
        Processa apenas mensagens do dia atual.
        """
        total_start_time = time.time()
        async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
            for chat in self.chats:
                print(f"Processando mensagens do dia atual para o chat: {chat}")
                # offset_date = self.fuso_correto
                offset_date = (self.fuso_correto - timedelta(days=1))
                await self.process_chat(client, chat, offset_date)
        total_elapsed_time = time.time() - total_start_time  # Tempo total decorrido
        print(f"Tempo total de execução: {total_elapsed_time:.2f} segundos")
