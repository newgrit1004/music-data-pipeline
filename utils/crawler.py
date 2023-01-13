import re
import time
from typing import List, Union

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By

from model.song import Song


class MelonCrawler:
    """Crawling song lyrics on Melon.

    Attributes:
        self.driver (Youtube): a Youtube object
        self.signer_name (str): 현재 크롤링할 가수 이름
        self.artist_id (str): 현재 크롤링할 가수의 artist_id
        self.soup (BeautifulSoup): 주어진 url의 html을 html.parser를 이용하여 파싱하여 생성된 BeautifulSoup 객체
        self.song_id_list (): self.artist_id를 이용하여 아티스트 채널에 들어갔을 때, pageindex에 존재하는 song의 id list, 최대 50개
        self.song_title_list (): self.artist_id를 이용하여 아티스트 채널에 들어갔을 때, pageindex에 존재하는 song의 title list, 최대 50개
        self.next_page_index_list (): self.artist_id를 이용하여 아티스트 채널에 들어갔을 때, 페이지 하단에 다음 페이지로 이동할 경우의 index를 의미.
                                    2022년 9월 27일 기준으로 멜론 아티스트 곡정보에서 1페이지당 최대 50개 단위로 나뉨.
    """

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        # DevToolsActivePort file doesn't exist error 방지
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Headless 탐지 방지
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"
        chrome_options.add_argument("user-agent={0}".format(user_agent))

        # 웹브라우저 설정
        path = "/root/workspace/music-data-pipeline/chromedriver"
        self.driver = webdriver.Chrome(path, chrome_options=chrome_options)
        self.singer_name = ""
        self.artist_id = None

    def get_html(self, url: str):
        """Get a BeautifulSoup object from given url.

        Args:
            url (str): url to parse html to generate BeautifulSoup.
        """
        self.driver.get(url)
        html = self.driver.page_source
        self.soup = BeautifulSoup(html, "html.parser")
        return self.soup

    @property
    def singer_name(self):  # getter
        return self._singer_name

    @singer_name.setter
    def singer_name(self, name: str):  # setter
        self._singer_name = name

    def search_singer(self, singer_name: str):
        """Set self.soup using singer_name and search_url.

        Args:
            singer_name (str): singer_name
        """
        search_url = f"https://www.melon.com/search/total/index.htm?q={singer_name}"
        self.get_html(search_url)

    def get_artist_id(self):
        """Find artist id of singer_name using self.soup."""
        href = self.soup.find("a", {"class": "atistname"}).get("href")
        artist_id_twice = re.sub(r"[^0-9]", "", href)
        self.artist_id = artist_id_twice[: len(artist_id_twice) // 2]
        return self.artist_id

    def get_song_list(
        self, page_index: int = 1
    ) -> Union[List[str], List[str], List[str]]:
        """Get the song_id_list, song_title_list and next_page_index_list using self.artist_id and page_index.

        Note:
            song_list_url (str): 멜론 아티스트 채널에서 '곡' 버튼을 누른 뒤 최신순 상태였을 때 1번째 페이지의 url.
            아티스트 곡정보의 최신순 첫번째 페이지를 기준으로 self.song_id_list, self.song_title_list,
            self.next_page_index_list를 고정하도록 한다.
            최신순 첫번째 페이지에서 추후에 발견되지 않았을 경우 self.next_page_idnex를 이용하여
            다른 페이지에서 원하는 곡 정보가 존재하는지 체크하도록 한다.

        Args:
            page_index (str): page_index, default value=1
        """
        song_list_url = f"https://www.melon.com/artist/song.htm?artistId={self.artist_id}#params%5BlistType%5D=A&params%5BorderBy%5D=ISSUE_DATE&params%5BartistId%5D={self.artist_id}&po=pageObj&startIndex={page_index}"
        soup = self.get_html(song_list_url)

        # 첫번째 페이지 버튼 리스트로 고정
        song_info_button_list: ResultSet = soup.find_all(
            "a", {"class": "btn btn_icon_detail"}
        )  # 곡정보 버튼
        self.song_id_list = list(
            map(lambda x: re.sub(r"[^0-9]", "", x.get("href")), song_info_button_list)
        )
        self.song_title_list = list(
            map(
                lambda x: x.get("title").split("곡정보")[0].rstrip(), song_info_button_list
            )
        )
        # print(song_title_list)

        page_button_list: Tag = soup.find("span", {"class": "page_num"})
        self.next_page_index_list = list(
            map(
                lambda x: re.sub(r"[^0-9]", "", x.get("href")),
                page_button_list.select("a"),
            )
        )

        return self.song_id_list, self.song_title_list, self.next_page_index_list

    def get_lyrics(
        self, target_song: str, song_id_list: List[str], song_title_list: List[str]
    ) -> Song:
        """Get lyrics of target_song using song_id.

        Note:
            MelonCrawler() 객체를 생성한 뒤, get_song_list를 이용하여 첫번째 페이지 기본 세팅을 한 뒤,
            find_target_song_lyrics에서 target_song을 찾을 때까지 get_lyrics 함수를 호출한다.

        Args:
            target_song (str): 찾고자하는 노래
            song_id_url (List(str)): 멜론 아티스트 채널 곡에 있는 url에 존재하는 모든 song의 id 정보
            song_title_list (List(str)): 멜론 아티스트 채널 곡에 있는 url에 존재하는 모든 song의 title 정보

        Return:
            Song object

        Examples:
            >>> print(song.total_lyric)
            '이 밤 그날의 반딧불을 당신의 창 가까이 보낼게요...'
            >>> print(song.lyric_enter_segment)
            ['이 밤 그날의 반딧불을', '당신의 창 가까이 보낼게요', ... ]
        """
        song = Song()
        for song_id, song_title in zip(song_id_list, song_title_list):
            if target_song in song_title:
                lyric_url = f"https://www.melon.com/song/detail.htm?songId={song_id}"
                self.driver.get(lyric_url)
                # 가사 펼치기 버튼 클릭
                self.driver.find_element(
                    By.CSS_SELECTOR, ".button_more.arrow_d"
                ).click()
                # 가사 클릭
                lyric = self.driver.find_element(By.CSS_SELECTOR, ".lyric.on")
                lyric_enter_segment = list(filter(None, lyric.text.split("\n")))
                total_lyric = re.sub("\n", " ", lyric.text)
                # print(total_lyric)
                song.song_title = song_title
                song.total_lyric = total_lyric.lower()
                song.lyric_enter_segment = lyric_enter_segment
        return song

    def find_target_song_lyrics(self, target_song: str) -> Song:
        """Find all pages of artist song info to get lyrics of target song

        Args:
            target_song (str): 찾고자하는 노래

        Return:
            Song object

        Examples:
            >>> print(song.total_lyric)
            '이 밤 그날의 반딧불을 당신의 창 가까이 보낼게요...'
            >>> print(song.lyric_enter_segment)
            ['이 밤 그날의 반딧불을', '당신의 창 가까이 보낼게요', ... ]
        """
        if target_song in self.song_title_list:
            try:
                song = self.get_lyrics(
                    target_song, self.song_id_list, self.song_title_list
                )
            except UnboundLocalError:
                print("사이트 측에서 crawling bot으로 감지하여 가사 탐색이 되지 않습니다")
        else:
            for next_index in self.next_page_index_list:
                # 원하는 페이지가 안나와서 임시로 저렇게 설정함.
                self.song_id_list, self.song_title_list, _ = self.get_song_list(
                    page_index=next_index
                )
                time.sleep(5)
                self.song_id_list, self.song_title_list, _ = self.get_song_list(
                    page_index=next_index
                )

                if target_song in self.song_title_list:
                    print(f'next_index : {next_index}')
                    try:
                        song = self.get_lyrics(
                            target_song, self.song_id_list, self.song_title_list
                        )
                    except UnboundLocalError:
                        print("사이트 측에서 crawling bot으로 감지하여 가사 탐색이 되지 않습니다")
        return song
