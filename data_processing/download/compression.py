import os
import subprocess
import zstandard as zstd

def compress_with_ffmpeg(input_file, output_file):
    """
    Recompressão de vídeos usando FFmpeg.
    Processo acontece em paralelo com -present slow para melhor desempenho da compressão
    """
    try:
        print(f"Recomprimindo vídeo: {output_file}")
        subprocess.run(
            [
                "ffmpeg",
                "-i", input_file,
                "-vcodec", "libx265",
                "-crf", "28",
                "-preset", "slow",
                "-acodec", "aac",
                "-b:a", "128k",
                output_file,
            ],
            check=True
        )
        os.remove(input_file)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Erro na recompressão de vídeo: {e}")
        return None


def compress_with_zstd(input_file, output_file):
    """
    Compressão de arquivos usando zstandard.
    """
    try:
        print(f"Comprimindo mídia com ZSTD: {output_file}")
        with open(input_file, "rb") as temp_file, open(output_file, "wb") as compressed_file:
            compressor = zstd.ZstdCompressor(level=15, threads=4)
            compressor.copy_stream(temp_file, compressed_file)
        os.remove(input_file)
        return output_file
    except Exception as e:
        print(f"Erro ao comprimir mídia com ZSTD: {e}")
        return None
