import pickle
from collections import defaultdict
from pathlib import Path, PosixPath
from typing import Dict, List, Union
from pathlib import Path, PosixPath
import time
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_song_dict() -> Dict[str, Dict[str, Union[str, List[str]]]]:
    """Load crawling lyrics pickle files from root directory."""
    with open("./file/pickle/final_song_lyric_dict.pkl", "rb") as f:
        song_dict = pickle.load(f)
    return song_dict


def load_scene_time_info() -> Dict[str, List[Dict[str, float]]]:
    """Load scene time info dict from pickle.

    Examples:
        >>> print(scene_info_time_dict['에필로그'])
        [{'start': 0.0, 'end': 20.987654320987655},
          {'start': 20.987654320987655, 'end': 31.631631631631635},
          {'start': 31.631631631631635, 'end': 41.70837504170838},...]
    """
    with open("./file/pickle/scene_info_time_dict.pkl", "rb") as f:
        scene_info_time_dict = pickle.load(f)
    return scene_info_time_dict


def findall(sub: str, string: str):
    """
    reference : https://stackoverflow.com/questions/3873361/finding-multiple-occurrences-of-a-string-within-a-string-in-python
    >>> text = "Allowed Hello Hollow"
    >>> tuple(findall('ll', text))
    (1, 10, 16)
    """
    index = 0 - len(sub)
    try:
        while True:
            index = string.index(sub, index + len(sub))
            yield index
    except ValueError:
        pass


def text_cosine_similarity(sentences: List[str]):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(sentences)

    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]


def load_lyric_url():
    with open("./file/yaml/song_url.yml") as f:
        song_lyric_urls = yaml.safe_load(f)
    return song_lyric_urls


def makedirs(dir_name: str) -> PosixPath:
    """Generate a new directory and return its folder name.
    Args:
        dir_name (str): directory name
    Returns:
        PosixPath
    """
    new_path = Path(__file__).parents[1] / dir_name
    new_path.mkdir()
    return new_path


class time_measure:
    def __init__(self, func) :
        self.start_time = time.time()
        self.func = func
    def __call__(self, *args, **kwargs) :
        print(f"{self.func.__name__}{args} stated at {time.strftime('%X')}")
        self.func(*args, **kwargs)
        finish_time = time.time()
        print(f"{self.func.__name__}{args} finish at {time.strftime('%X')}, total:{finish_time-self.start_time} sec(s)")