import os
from dotenv import load_dotenv
import asyncio
from jobs.telegram_downloader import TelegramDownloader
from jobs.telegram_simple_downloader import TelegramDownloaderSimple

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "None")

def execute_full_download(chats):
    downloader = TelegramDownloader(chats)
    asyncio.run(downloader.start())

def execute_simple_download(chats):
    downloader_simple = TelegramDownloaderSimple(chats)
    asyncio.run(downloader_simple.start())

if __name__ == "__main__":
    chats = ["Portalnoticiasceara"]
    mode = os.getenv("DOWNLOAD_MODE", "simple")

    if mode == "full":
        execute_full_download(chats)
    else:
        execute_simple_download(chats)
