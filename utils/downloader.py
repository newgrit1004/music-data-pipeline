import os

from pytube import Playlist, YouTube

# from utils.utils import makedirs


class YoutubeSongDownloader:
    """Download a single song from youtube url.

    Attributes:
        self.yt (Youtube): a Youtube object
    """

    def __init__(self, url: str):
        """Inits YoutubeSongDownloader with youtube url."""
        self.yt = YouTube(url)
        self.yt.streams.filter(only_audio=True)

    def download(self, download_folder_name: str):
        """Download a song from the url.

        Args:
            download_folder_name (str): a folder path where a song will be downloaded.
        """
        # _ = makedirs(download_folder_name)
        self.yt.streams.filter(only_audio=True).first().download(
            f"./{download_folder_name}"
        )
        print("Single song downloaded complete")


class YoutubeVideoDownloader:
    """Download a single video from youtube url.

    Attributes:
        self.yt (Youtube): a Youtube object
    """

    def __init__(self, url: str):
        """Inits YoutubeVideoDownloader with youtube url."""
        self.yt = YouTube(url)
        self.yt.streams.filter(progressive=True, res="720p")

    def download(self, download_folder_name: str):
        """Download a song from the url.

        Args:
            download_folder_name (str): a folder path where a video will be downloaded.
        """
        # _ = makedirs(download_folder_name)
        self.yt.streams.filter(progressive=True, res="720p").first().download(
            f"{download_folder_name}"
        )
        print("Single song downloaded complete")


# TODO: makedirs 부분 수정 필요.
# class PlaylistDownloader:
#     """Download all songs of the playlist from youtube playlist url.

#     Attributes:
#         self.pl (Playlist): a Playlist object
#     """

#     def __init__(self, url: str):
#         """Inits PlaylistSongDownloader with youtube playlist url."""
#         self.pl = Playlist(url)
#         print(f"Total number of the videos : {len(self.pl.video_urls)}")

#     def download(self, download_folder_name: str):
#         """Download songs from the playlist url.

#         Args:
#             download_folder_name (str): a folder path where songs will be downloaded.

#         Raises:
#             VideoUnavailable : loading single video error.
#             KeyError : 'streamingData' for video removed for violating youtube's terms of service.
#         """
#         _ = makedirs(download_folder_name)
#         for url in self.pl.video_urls:
#             try:
#                 video = YouTube(url)
#             except VideoUnavailable:
#                 pass
#             else:
#                 try:
#                     video.streams.filter(only_audio=True).first().download(
#                         f"./{download_folder_name}"
#                     )
#                 except KeyError:
#                     pass
