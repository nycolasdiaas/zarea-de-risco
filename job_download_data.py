from telethon.sync import TelegramClient
import datetime
import os
from tqdm import tqdm
import json
import zstandard as zstd
import tempfile
from dotenv import load_dotenv

from exceptions import CompressionException

load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID", 0))
api_hash = os.getenv("TELEGRAM_API_HASH", "None")

chats = ["Portalnoticiasceara"]
base_output_folder = "./downloads/"
df_list = []
processed_messages = []


def save_media(message, media_folder):
    if message.media:
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

            if media_type is None or file_name is None:
                return None, None

            # file_path = os.path.join(media_folder, file_name)
            compressed_file_name = f"{file_name}.zstd"
            compressed_file_path = os.path.join(media_folder, compressed_file_name)

            if os.path.exists(compressed_file_name):
                print(f"A mídia já foi baixada e comprimida: {compressed_file_name}")
                return compressed_file_name, media_type

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir)
                total_size = (
                    message.media.size if hasattr(message.media, "size") else None
                )

                if total_size:
                    with tqdm(
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        desc=f"Baixando {file_name}",
                    ) as pbar:
                        temp_path = message.download_media(
                            file=temp_path,
                            progress_callback=lambda d, t: pbar.update(
                                d - pbar.n if t else 0
                            ),
                        )
                else:
                    temp_path = message.download_media(file=temp_path)

                # Comprime o arquivo e salva no destino final
                with open(compressed_file_path, "wb") as compressed_file:
                    compressor = zstd.ZstdCompressor(level=3, threads=4)
                    with open(temp_path, "rb") as temp_file:
                        compressor.copy_stream(temp_file, compressed_file)

                # if total_size:
                #         with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Baixando e comprimindo {file_name}") as pbar:
                #             with open(compressed_file_path, 'wb') as compressed_file:
                #                 compressor = zstd.ZstdCompressor(level=3, threads=4)
                #                 # file_path = message.download_media(file=file_path, progress_callback=lambda d, t: pbar.update(d - pbar.n if t else 0))
                #                 with message.download_media(progress_callback=lambda d, t: pbar.update(d-pbar.n if t else 0)) as file:
                #                     compressor.copy_stream(file, compressed_file)
                # else:
                #     # file_path = message.download_media(file=file_path)
                #     with open(compressed_file_path, 'wb') as compressed_file:
                #         compressor = zstd.ZstdCompressor(level=3, threads=4)
                #         with message.download_media() as file:
                #             compressor.copy_stream(file, compressed_file)
            print(f"Arquivo comprimido salvo em: {compressed_file_path}")
            return compressed_file_path, media_type

        except Exception as e:
            raise CompressionException(f"Erro ao baixar e comprimir mídia: {e}")
    return None, None


os.makedirs(base_output_folder, exist_ok=True)

for chat in chats:
    group_folder = os.path.join(base_output_folder, chat)

    with TelegramClient("session_name", api_id, api_hash) as client:
        all_messages = list(
            client.iter_messages(
                chat,
                offset_date=datetime.date.today() - datetime.timedelta(days=2),
                reverse=True,
            )
        )

        with tqdm(
            total=len(all_messages),
            desc="Processando mensagens e baixando mídias",
            unit="msg",
            position=0,
            leave=True,
        ) as pbar:
            for message in all_messages:
                print(f"\nProcessando mensagem ID: {message.id}")

                media_folder = f"{group_folder}/{str(message.date.date())}/media/"
                os.makedirs(media_folder, exist_ok=True)
                media_path, media_type = save_media(message, media_folder)

                # Verificar se a mensagem é uma resposta
                reply_to_message = None
                if message.reply_to:
                    try:
                        reply_to_message_id = message.reply_to.reply_to_msg_id
                        reply_to_message = client.get_messages(
                            chat, ids=reply_to_message_id
                        )
                    except Exception as e:
                        print(f"Erro ao buscar mensagem original: {e}")
                        reply_to_message = None

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
                    "date": (message.date - datetime.timedelta(hours=3)).isoformat(),
                    "message": message.text,
                    "reply_to": {
                        "reply_to_msg_id": (
                            message.reply_to.reply_to_msg_id
                            if message.reply_to
                            else None
                        ),
                        "reply_to_message_text": (
                            reply_to_message.text if reply_to_message else None
                        ),
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
                                        message.media.photo.date.isoformat()
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
                        message.edit_date.isoformat() if message.edit_date else None
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

                processed_messages.append(data)
                pbar.update(1)

                output_file = f"{group_folder}/{str(message.date.date())}/metadata.json"

                with open(output_file, "w", encoding="utf-8") as json_file:
                    json.dump(
                        processed_messages, json_file, ensure_ascii=False, indent=4
                    )
                print(f"\nMensagens processadas salvas em: {output_file}")
