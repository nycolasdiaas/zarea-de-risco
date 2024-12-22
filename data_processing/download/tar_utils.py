import os
import tarfile
import zstandard as zstd

def create_tar_from_zstd_files(media_folder):
    tar_file_path = os.path.join(media_folder, "media.tar")
    tar_compressed_path = f"{tar_file_path}.zstd"

    if os.path.exists(tar_compressed_path):
        print(f"Arquivo TAR.ZSTD já existente: {tar_compressed_path}")
        return

    try:
        zstd_files = [f for f in os.listdir(media_folder) if f.endswith(".zstd")]
        if not zstd_files:
            print(f"Nenhum arquivo .zstd encontrado em: {media_folder}")
            return

        print(f"Agrupando arquivos .zstd em: {tar_compressed_path}")

        with tarfile.open(tar_file_path, "w") as tar:
            for file_name in zstd_files:
                file_path = os.path.join(media_folder, file_name)
                tar.add(file_path, arcname=file_name)

        with open(tar_file_path, "rb") as tar_file, open(tar_compressed_path, "wb") as compressed_file:
            compressor = zstd.ZstdCompressor(level=15)
            compressor.copy_stream(tar_file, compressed_file)

        os.remove(tar_file_path)
        for file_name in zstd_files:
            os.remove(os.path.join(media_folder, file_name))

    except Exception as e:
        print(f"Erro ao agrupar arquivos em TAR.ZSTD: {e}")
