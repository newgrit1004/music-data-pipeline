from typing import List


class Song:
    """An object made by crawling.

    Attributes:
        self.singer_name (str): 가수 이름
        self.song_title (str): 노래 이름
        self.total_lyric (str): 노래의 전체 가사, '\n'을 공백(' ')으로 치환하였음.
        self.lyric_enter_segment (str): 노래의 전체 가사를 '\n'을 기준으로 split하였음.
    """

    def __init__(self) -> None:
        self.singer_name: str = None
        self.song_title: str = None
        self.total_lyric: str = None
        self.lyric_enter_segment: List[str] = None
