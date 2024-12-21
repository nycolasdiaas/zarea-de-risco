import os
import json
from datetime import datetime, timedelta
import zstandard as zstd
from queue import Queue
from threading import Thread, Lock
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "None")
BASE_OUTPUT_FOLDER = "./downloads"
lock = Lock()

class TelegramDownloader:
    def __init__(self, chats, max_threads=4):
        self.chats = chats
        self.messages_queue = Queue()
        self.max_threads = max_threads
        self.fuso_correto = datetime.utcnow() - timedelta(hours=3)
    
    def save_media(self, message, media_folder):
        """
        Salvando as mídias das mensagens
        """
        
        if not message.media:
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
            
            compressed_file_name = f'{file_name}_.zstd'
            compressed_file_path = os.path.join(media_folder, compressed_file_name)
            
            # Arquivos existentes
            if os.path.exists(compressed_file_path):
                return compressed_file_path, media_type
            
            original_file_path = os.path.join(media_folder, file_name)
            os.makedirs(media_folder, exist_ok=True)
            
            message.download_media(file=original_file_path)
            
            with open(compressed_file_path, 'wb') as compressed_file:
                compressor = zstd.ZstdCompressor(level=3, threads=4)
                with open(original_file_path, 'rb') as temp_file:
                    compressor.copy_stream(temp_file, compressed_file)
            
            # os.remove(original_file_path)
            return compressed_file_path, media_type
        except Exception as e:
            print(f"Erro ao salvar {e}")
            return None, None
        
    def process_message(self, message, chat_folder):
        """
        Processando messagem unitaria
        """
        message_date = (message.date - timedelta(hours=3)).date()
        media_folder = os.path.join(chat_folder, str(message_date), 'media')
        os.makedirs(media_folder, exist_ok=True)
        media_path, media_type = self.save_media(message, media_folder)
        
        
        data = {
            "id": message.id,
            "date": (message.date - timedelta(hours=3)).isoformat(),
            "message": message.text,
            "media_path": media_path,
            "media_type": media_type,
        }
        return message_date, data
    
    def worker(self, chat_folder):
        """
        Processando mensagens em queue
        """
        while not self.messages_queue.empty():
            message = self.messages_queue.get()
            try:
                message_date, data = self.process_message(message, chat_folder)
                output_file = os.path.join(chat_folder, str(message_date), 'metadata.json')
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                with lock: # Bloqueando a escrita do json para não acontecer problema devido aos multiplos threads em execução
                    if os.path.exists(output_file):
                        with open(output_file, 'r', encoding='utf-8') as f:
                            messages = json.load(f)
                    else:
                        messages = []
                    
                    messages.append(data)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(messages, f, ensure_ascii=False, indent=4)
                    
            except Exception as e:
                print(f'Erro ao processar mensagem: {e}')
            finally:
                self.messages_queue.task_done()
                
    def process_chat(self, client, chat):
        """
        Processando todas as mensagens do chat
        """
        
        chat_folder = os.path.join(BASE_OUTPUT_FOLDER, chat)
        os.makedirs(chat_folder, exist_ok=True)
        
        all_messages = list(
            client.iter_messages(chat, offset_date=self.fuso_correto - timedelta(days=1), reverse=True)
        )
        for message in all_messages:
            self.messages_queue.put(message)
        
        threads = []
        for _ in range(self.max_threads):
            t = Thread(target=self.worker, args=(chat_folder,))
            t.start()
            threads.append(t)
            
        for t in threads:
            t.join()
            
    def start(self):
        """
        Iniciando o processo de download e processamento
        """
        with TelegramClient("session_name", API_ID, API_HASH) as client:
            for chat in self.chats:
                print(f'Processando chat: {chat}')
                self.process_chat(client, chat)
                
if __name__ == '__main__':
    chats = ["Portalnoticiasceara"]
    
    print(API_ID, API_HASH)
    downloader =  TelegramDownloader(chats, max_threads=4)
    downloader.start()
        