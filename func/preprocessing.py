from pydub.silence import detect_nonsilent
from pydub import AudioSegment
from typing import List, Dict, Any
import os
from utils.utils import makedirs
from pathlib import Path

def normalize_amplitude(sound:AudioSegment, target_dBFS:float)->AudioSegment:
    """Achieve normalization of peak volume.

    Args:
        sound (AudioSegment): an AudioSegment object
        target_dBFS (float): if target_dbFS is lower than 0, the sound will be lowered.
                                Otherwise, the sound will be raised.

    Returns:
        AudioSegment object : raised or lowered determined by target_dBFS
    """
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)


def get_time_segments(audio_file:AudioSegment, criterion:int)->List[Dict[str, Any]]:
    """Achieve normalization of peak volume.

    Args:
        audio_file (AudioSegment): an AudioSegment object
        criterion (int): 비침묵과 침묵 사이의 간격 기준, 단위는 ms

    Returns:
        List[Dict[str, Any]]

    Examples:
        >>> print(get_time_segments(normalized_sound, 1500))
        [{'start': 0, 'end': 18655, 'tag': '침묵'},
        {'start': 18655, 'end': 30300, 'tag': '비침묵'},
        {'start': 30100, 'end': 31915, 'tag': '침묵'},
        {'start': 31715, 'end': 65853, 'tag': '비침묵'},
        ...]
    """
    intervals_jsons = []

    min_silence_length = 70

    #주어진 오디오의 모든 nonsilience segment의 시작점과 끝점을 가져온다.
    #silence_thresh = the upper bound for how quiet is slient in dBFS
    intervals = detect_nonsilent(audio_file,
                               min_silence_len=min_silence_length,
                               silence_thresh=-32.64)


    if intervals[0][0] != 0:
        intervals_jsons.append({'start':0,'end':intervals[0][0],'tag':'silence'})

    non_silence_start, before_silence_start = intervals[0][0], intervals[0][1]

    for interval in intervals:
        if (interval[0] - before_silence_start) >= criterion:
            intervals_jsons.append({'start':non_silence_start,'end':(before_silence_start+200),'tag':'nonsilence'})
            non_silence_start = interval[0]-200
            intervals_jsons.append({'start':before_silence_start,'end':interval[0],'tag':'silence'})
        before_silence_start = interval[1]

    if non_silence_start != len(audio_file):
        intervals_jsons.append({'start':non_silence_start,'end':len(audio_file),'tag':'nonsilence'})

    return intervals_jsons


def voice_isolation(wav_file:str, stems:int=2):
    """Isolate vocal and MR using spleeter.

    Args:
        wav_file (str): a single wav file path.
        stems (int): default value = 2(vocal, MR). available values are 2,4,5

    TODO:
        * make exception of stems.
    """
    output_directory = './vocal_isolation'
    command = r'spleeter separate -p spleeter:' + \
    str(stems)+f'stems -o {output_directory} '+wav_file
    print(command)
    os.system(command)



def nonsilence_segmentation(vocal_wav:str):
    """Get nonsilence segmenations for a given song

    Args:
        wav_file (str): a single wav file path.

    TODO:
        * os -> pathlib
        * use config class later
        * need more segmentation for long segments
    """
    sound = AudioSegment.from_file(vocal_wav, "wav")
    normalized_sound = normalize_amplitude(sound, -20.0)
    interval_jsons = get_time_segments(normalized_sound, 1500)
    song_name = os.path.dirname(vocal_wav).split('/')[2]
    dir_name = Path(f'TTS_training_data/{song_name}')
    saved_path = makedirs(dir_name)

    for json in interval_jsons:
        if json['tag'] == 'nonsilence':
            start = json['start']
            end = json['end']
            file_name = f'{song_name}_{start}_{end}.mp3'
            normalized_sound[start:end].export(os.path.join(saved_path, file_name))
