import glob
import os
import re

from pydub import AudioSegment


def mp4_to_mp3(download_path: str):
    """Convert a single mp4 file into a mp3 file.

    Args:
        download_path (str): Path that contains downloaded mp4 files.
    """
    files = glob.glob(f"./{download_path}/*.mp4")
    for x in files:
        if not os.path.isdir(x):
            filename = os.path.splitext(x)
            try:
                os.rename(x, filename[0] + ".mp3")
            except:
                pass
    print("youtube mp4 to mp3 convert complete")


def youtube_mp3_to_wav(src: str, dst: str = None):
    """Convert a single mp3 file into a wav format file.

    Note:
        The input mp3 files were downloaded from youtube in mp4 file format at the first time.
        So, container format is mpeg4 and the mp3 files contain AAC audio codec.

    Args:
        src (str): a mp3 file path
        dst (str): a wave file path

    Examples:
        >>> youtube_mp3_to_wav('./playlist_download/Knees (무릎).mp3')
        Generated wav file path = './playlist_download/무릎.mp3'
    """

    try:
        sound = AudioSegment.from_file(src, "mp3")
    except:
        sound = AudioSegment.from_file(src, format="mp4")
    if not dst:
        directory, filename = os.path.split(src)
        filename, ext = os.path.splitext(filename)
        filename = re.sub(r"[^가-힣]", "", filename)
        filename = re.sub(" ", "", filename)
        dst = os.path.join(directory, filename + ".wav")
    sound.export(dst, format="wav")
    print("youtube mp3 to wav convert complete")
