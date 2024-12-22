import time
import asyncio
from download.downloader import TelegramDownloader

def execute_download_job(chats):
    """
    Job principal para execução do processo de download/
    """
    downloader = TelegramDownloader(chats, max_workers=10)
    start_time = time.time()
    asyncio.run(downloader.start())
    end_time = time.time()
    print(f"Tempo total de execução: {end_time - start_time:.2f} segundos")
