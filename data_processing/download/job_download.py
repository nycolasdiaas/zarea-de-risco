import os
import json
from datetime import datetime, timedelta
import zstandard as zstd
import asyncio
from telethon import TelegramClient
from telethon.errors import RPCError
from dotenv import load_dotenv
import time
import tarfile

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "None")
BASE_OUTPUT_FOLDER = "./downloads"

class TelegramDownloader:
    def __init__(self, chats, max_workers=10):
        self.chats = chats
        self.max_workers = max_workers
        self.fuso_correto = datetime.utcnow() - timedelta(hours=3)
        self.queue = asyncio.Queue()

    async def retry_download(self, message, file_path, retries=3, delay=2):
        """
        Realiza múltiplas tentativas para baixar mídia
        
        conexão ou sessão podem ocasionar problemas
        """
        for attempt in range(retries):
            try:
                print(f"Tentativa {attempt + 1} para baixar: {file_path}")
                result = await message.download_media(file=file_path)
                if result and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    return True
            except RPCError as e:
                print(f"Erro RPC no download: {e}")
            except Exception as e:
                print(f"Erro desconhecido no download: {e}")
            await asyncio.sleep(delay)
        return False

    async def save_media(self, message, media_folder):
        """
        Salvando as mídias das mensagens.
        processo de download e compressão juntos, dessa forma economiza tempo e disco,
        pois o teremos os arquivos em seu tamanho original por menos tempo
        """
        if not message.media:
            print(f"Mensagem ID {message.id} não contém mídia ou a mídia não está disponível.")
            return None, None

        try:
            media_type = None
            file_name = None
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

            if not media_type or not file_name:
                return None, None

            compressed_file_name = f"{file_name}.zstd"
            compressed_file_path = os.path.join(media_folder, compressed_file_name)

            if os.path.exists(compressed_file_path):
                print(f"Arquivo já processado: {compressed_file_path}")
                return compressed_file_path, media_type

            original_file_path = os.path.join(media_folder, file_name)
            os.makedirs(media_folder, exist_ok=True)

            # Tentar baixar a mídia
            print(f"Baixando mídia: {original_file_path}")
            if not await self.retry_download(message, original_file_path):
                print(f"Erro: Falha no download ou arquivo vazio para: {original_file_path}")
                return None, None

            # Comprimir o arquivo
            print(f"Comprimindo mídia: {compressed_file_path}")
            with open(compressed_file_path, "wb") as compressed_file:
                compressor = zstd.ZstdCompressor(level=15, threads=4)
                with open(original_file_path, "rb") as temp_file:
                    compressor.copy_stream(temp_file, compressed_file)

            if os.path.exists(original_file_path):
                os.remove(original_file_path)

            return compressed_file_path, media_type
        except Exception as e:
            print(f"Erro ao salvar mídia: {e}")
            return None, None

    async def process_message(self, message, chat_folder):
        """
        Processando mensagem unitária
        """
        message_date = (message.date - timedelta(hours=3)).date()
        media_folder = os.path.join(chat_folder, str(message_date), "media")
        os.makedirs(media_folder, exist_ok=True)

        media_path, media_type = await self.save_media(message, media_folder)

        data = {  # temporario
            "id": message.id,
            "date": (message.date - timedelta(hours=3)).isoformat(),
            "message": message.text,
            "media_path": media_path,
            "media_type": media_type,
        }
        return message_date, data

    async def worker(self, chat_folder):
        """
        Processando mensagens em queue.
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
        """
        Agrupa mídias compactadas por dia em arquivos TAR.ZSTD dentro da pasta correta.
        """
        for root, dirs, _ in os.walk(chat_folder):
            # Filtrar apenas subpastas com estrutura de data
            for folder in dirs:
                date_folder = os.path.join(root, folder)
                
                # Verificar se estamos dentro da estrutura correta de data
                if not os.path.isdir(date_folder) or not folder.startswith("20"):
                    continue

                media_folder = os.path.join(date_folder, "media")
                if not os.path.exists(media_folder):
                    continue

                tar_file_path = os.path.join(media_folder, "media.tar")
                tar_compressed_path = f"{tar_file_path}.zstd"

                # Verificar se o arquivo já existe
                if os.path.exists(tar_compressed_path):
                    print(f"Arquivo TAR.ZSTD já existente: {tar_compressed_path}")
                    continue

                print(f"Agrupando mídias em: {tar_compressed_path}")
                try:
                    # Criar o arquivo TAR
                    with tarfile.open(tar_file_path, "w") as tar:
                        files_to_remove = []
                        for file_name in os.listdir(media_folder):
                            file_path = os.path.join(media_folder, file_name)
                            if file_path.endswith(".zstd"):
                                tar.add(file_path, arcname=file_name)
                                files_to_remove.append(file_path)

                    # Comprimir o TAR com zstd
                    if os.path.exists(tar_file_path):
                        with open(tar_file_path, "rb") as tar_file:
                            with open(tar_compressed_path, "wb") as compressed_file:
                                compressor = zstd.ZstdCompressor(level=3)
                                compressor.copy_stream(tar_file, compressed_file)

                        # Remover o TAR não comprimido
                        os.remove(tar_file_path)

                        # Remover os arquivos originais
                        for file_path in files_to_remove:
                            os.remove(file_path)
                    else:
                        print(f"Erro: Arquivo TAR não foi criado corretamente em {tar_file_path}")

                except Exception as e:
                    print(f"Erro ao agrupar mídias em TAR.ZSTD: {e}")

    async def process_chat(self, client, chat):
        """
        Processando todas as mensagens do chat.
        """
        chat_folder = os.path.join(BASE_OUTPUT_FOLDER, chat)
        os.makedirs(chat_folder, exist_ok=True)

        async for message in client.iter_messages(chat, offset_date=self.fuso_correto - timedelta(days=0), reverse=True):
            await self.queue.put(message)

        workers = [asyncio.create_task(self.worker(chat_folder)) for _ in range(self.max_workers)]

        await self.queue.join()
        for _ in range(self.max_workers):
            await self.queue.put(None)
        await asyncio.gather(*workers)
        
        await self.group_media_by_date(chat_folder)

    async def start(self):
        """
        Iniciando o processo de download e processamento.
        """
        async with TelegramClient("session_name", API_ID, API_HASH) as client:
            for chat in self.chats:
                print(f"Processando chat: {chat}")
                await self.process_chat(client, chat)


if __name__ == "__main__":
    chats = ["Portalnoticiasceara"]

    downloader = TelegramDownloader(chats, max_workers=10)
    
    start_time = time.time()
    asyncio.run(downloader.start())
    end_time = time.time()

    exec_total_time = end_time - start_time
    print(f"Tempo total de execução: {exec_total_time:.2f} segundos")
