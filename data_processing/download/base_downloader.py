import os
import asyncio
from datetime import datetime, timedelta
import json
from telethon.tl.types import PeerChannel, PeerChat, PeerUser

# BASE_OUTPUT_FOLDER = './downloads'
BASE_OUTPUT_FOLDER = os.getenv("BASE_OUTPUT_FOLDER")

class BaseTelegramDownloader:
    def __init__(self, chats, max_workers=30):
        self.chats = chats
        self.max_workers = max_workers
        self.fuso_correto = datetime.now() - timedelta(hours=3)
        self.queue = asyncio.Queue()
        self.processed_grouped_ids = set()

    async def retry_download(self, message, file_path, retries=3, delay=2):
        """
        Realiza múltiplas tentativas de download.
        """
        for attempt in range(retries):
            try:
                print(f"Tentativa {attempt + 1} para baixar: {file_path}")
                result = await message.download_media(file=file_path)
                print("Resultado do download:", result)
                if result and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    return True
            except Exception as e:
                print(f"Erro no download: {e}")
            await asyncio.sleep(delay)
        return False

    async def save_media(self, message, media_folder):
        """
        Baixa mídia e retorna (file_path, media_type) ou (None, None) se falhar/não existir.
        """
        if not message.media:
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
            media_type = "document"
            file_name = f"document_{message.id}"
        elif hasattr(message.media, "audio"):
            media_type = "audio"
            file_name = f"audio_{message.id}.mp3"

        if not media_type or not file_name:
            return None, None

        os.makedirs(media_folder, exist_ok=True)
        file_path = os.path.join(media_folder, file_name)
        print(f"Baixando mídia: {file_path}")

        if not await self.retry_download(message, file_path):
            print(f"Erro ao baixar: {file_path}")
            return None, None
        relative_path = os.path.relpath(file_path, BASE_OUTPUT_FOLDER)
        
        return relative_path, media_type

    async def post_process_media(self, media_path, media_type, media_folder):
        """
        Gancho para processar mídias após download.
        (Pode ficar vazio ou sobrescrito.)
        """
        pass

    def build_message_dict(
        self,
        message,
        remove_media_path=True
    ):
        """
        Gera o dicionário completo de uma mensagem,
        mas SEM o 'media_path' individual (caso remove_media_path=True).
        Pois centralizaremos os caminhos em media_paths do dicionário principal.
        """
        data = {
            "id": message.id,
            "grouped_id": message.grouped_id,
            "peer_id": {
                "type": None,
                "id": None,
            },
            "date": (message.date - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
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
            "views": message.views,
            "forwards": message.forwards,
            "replies": (
                {
                    "replies": message.replies.replies if message.replies else None,
                    "replies_pts": message.replies.replies_pts if message.replies else None,
                    "comments": message.replies.comments if message.replies else None,
                    "channel_id": message.replies.channel_id if message.replies else None,
                    "max_id": None,
                    "read_max_id": None,
                }
                if message.replies
                else None
            ),
            "edit_date": (
                (message.edit_date - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
                if message.edit_date
                else None
            ),
            "reactions": [
                {
                    "reaction": r.reaction.emoticon,
                    "count": r.count,
                }
                for r in (message.reactions.results if message.reactions else [])
            ],
        }

        if isinstance(message.peer_id, PeerChannel):
            data["peer_id"]["type"] = "PeerChannel"
            data["peer_id"]["id"] = message.peer_id.channel_id
        elif isinstance(message.peer_id, PeerChat):
            data["peer_id"]["type"] = "PeerChat"
            data["peer_id"]["id"] = message.peer_id.chat_id
        elif isinstance(message.peer_id, PeerUser):
            data["peer_id"]["type"] = "PeerUser"
            data["peer_id"]["id"] = message.peer_id.user_id

        return data

    async def process_single_message(self, message, chat_folder):
        """
        Processa UMA mensagem isolada:
          - Baixa a mídia, se houver
          - Cria 'media_paths' com apenas 1 item (ou vazio)
          - Cria o dicionário normal de mensagem SEM media_path
          - Retorna (data_dict, date_str)
        """
        msg_date_str = (message.date - timedelta(hours=3)).strftime("%Y-%m-%d")
        media_folder = os.path.join(chat_folder, msg_date_str, "media")

        file_path, media_type = await self.save_media(message, media_folder)
        if file_path:
            await self.post_process_media(file_path, media_type, media_folder)
            media_paths = [file_path]
        else:
            media_paths = []

        data_dict = self.build_message_dict(message)
        data_dict["media_paths"] = media_paths

        return data_dict, msg_date_str

    async def process_grouped_messages(self, chat_folder, messages):
        """
        Recebe várias mensagens do mesmo grouped_id e retorna:
          (data_dict_da_principal, date_str).
        
        No dicionário principal:
          - "media_paths" conterá TODOS os caminhos (principal + submensagens)
          - "grouped_messages" terá a mesma estrutura, mas SEM media_path
        """
        first_msg = messages[0]
        grouped_id = first_msg.grouped_id

        if grouped_id in self.processed_grouped_ids:
            return None, None
        self.processed_grouped_ids.add(grouped_id)

        msg_date_str = first_msg.date.strftime("%Y-%m-%d")
        media_folder_main = os.path.join(chat_folder, msg_date_str, "media")

        # 1) Processa a "principal"
        main_file_path, main_media_type = await self.save_media(first_msg, media_folder_main)
        if main_file_path:
            await self.post_process_media(main_file_path, main_media_type, media_folder_main)

        main_dict = self.build_message_dict(first_msg)
        grouped_messages = []
        media_paths_total = []
        if main_file_path:
            media_paths_total.append(main_file_path)

        # 2) Submensagens
        for sub_m in messages[1:]:
            sub_date_str = sub_m.date.strftime("%Y-%m-%d")
            sub_media_folder = os.path.join(chat_folder, sub_date_str, "media")

            sub_file_path, sub_media_type = await self.save_media(sub_m, sub_media_folder)
            if sub_file_path:
                await self.post_process_media(sub_file_path, sub_media_type, sub_media_folder)
                media_paths_total.append(sub_file_path)

            sub_dict = self.build_message_dict(sub_m)
            grouped_messages.append(sub_dict)

        # 3) No "main_dict" final
        #    - "grouped_messages" terá a estrutura das submensagens
        #    - "media_paths" é a SOMA de todos os paths (principal e sub)
        main_dict["grouped_messages"] = grouped_messages
        main_dict["media_paths"] = media_paths_total

        return main_dict, msg_date_str

    async def process_group_or_solo(self, messages, chat):
        """
        Decide se é 1 mensagem isolada, várias isoladas ou um grupo (álbum).
        Retorna (data, date_str).
        """
        if not messages:
            return None, None

        chat_folder = os.path.join(BASE_OUTPUT_FOLDER, str(chat), "past_dates")
        os.makedirs(chat_folder, exist_ok=True)

        grouped_id = messages[0].grouped_id
        if grouped_id is not None and len(messages) > 1:
            return await self.process_grouped_messages(chat_folder, messages)
        if len(messages) == 1:
            return await self.process_single_message(messages[0], chat_folder)

        # grouped_id => cada uma vira um registro
        results = []
        final_date_str = None
        for m in messages:
            d, date_str = await self.process_single_message(m, chat_folder)
            results.append(d)
            final_date_str = date_str
        return results, final_date_str

    async def write_json(self, chat, data, date_str):
        chat_folder = os.path.join(BASE_OUTPUT_FOLDER, str(chat), "past_dates")
        date_folder = os.path.join(chat_folder, date_str)
        os.makedirs(date_folder, exist_ok=True)

        output_file = os.path.join(date_folder, "metadata.json")
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = []

        if isinstance(data, list):
            existing.extend(data)
        else:
            existing.append(data)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=4)

    async def worker(self, chat, client):
        """
        Worker que processa (grouped_id, [mensagens]) => (data, date_str)
        e grava no metadata.json do respectivo dia.
        """
        while True:
            item = await self.queue.get()
            if item is None:
                break
            try:
                grouped_id, msgs = item
                data, date_str = await self.process_group_or_solo(msgs, chat)
                if data is not None and date_str is not None:
                    await self.write_json(chat, data, date_str)
            except Exception as e:
                print(f"Erro ao processar mensagem/grupo: {e}")
            finally:
                self.queue.task_done()

    async def process_chat(self, client, chat, offset_date=None):
        """
        Lê todas as mensagens do chat, agrupa por grouped_id e enfileira.
        """
        print(f"Processando mensagens para o chat: {chat}")
        
        all_messages = []
        async for message in client.iter_messages(chat, offset_date=offset_date, reverse=True):
            all_messages.append(message)

        grouped_map = {}
        for m in all_messages:
            g_id = m.grouped_id
            grouped_map.setdefault(g_id, []).append(m)

        for g_id, msgs in grouped_map.items():
            await self.queue.put((g_id, msgs))

        workers = [asyncio.create_task(self.worker(chat, client)) for _ in range(self.max_workers)]
        await self.queue.join()
        for _ in range(self.max_workers):
            await self.queue.put(None)
        await asyncio.gather(*workers)

        await self.post_process_chat(chat)

    async def post_process_chat(self, chat):
        """
        Gancho opcional após terminar o chat.
        """
        pass
