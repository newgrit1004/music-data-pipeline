from pathlib import PosixPath
from typing import Any, Dict, List, Tuple, Union

import easyocr
import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from scenedetect import SceneManager, StatsManager, VideoManager
from scenedetect.detectors import ContentDetector
from scenedetect.scene_manager import save_images, write_scene_list_html

from model.scene import Scene


def trim_video(
    source_video_path: str, start_time: float, end_time: float, trimmed_video_path: str
):
    """Trim the video and generate trimmed video using start_time and end_time.

    Args:
        source_video_path (str): the path of the source video file you want to trim.
        start_time (float): start time(second) to cut from the source video.
        end_time (float): end time(second) to cut from the source video.
        trimmed_video_path (str): the path of trimmed video.
    """
    ffmpeg_extract_subclip(
        source_video_path, start_time, end_time, targetname=trimmed_video_path
    )


def crop_video(
    source_video_path: str, coordinates: Tuple[int], cropped_video_path: str
):
    """Crop the video and generate cropped video using resize_shape.

    Note:
        x1,y1 : top left corner
        x2,y2 : lower right corner

    Args:
        source_video_path (str): the path of the source video file you want to crop.
        coordinates (Tuple[int]): coordinates(x1, y1, x2, y2) to crop
        cropped_video_path (str): the path of cropped video.
    """
    x1, y1, x2, y2 = coordinates
    clip_resized = mp.VideoFileClip(source_video_path).crop(x1=x1, y1=y1, x2=x2, y2=y2)
    clip_resized.write_videofile(cropped_video_path)


def different_lyrics_detect(
    video_path: str, threshold: float, folder_name: str
) -> List[Dict[str, float]]:
    """Detect the scenes that have different lyrics from the cropped video and save them on ./scene folder.

    Note:
        한글 경로 인식 못함.

    Args:
        video_path (str): a cropped video file path
        threshold (float): a threshold value of scene detector

    Returns:
        List[Dict[str, float]]
    """
    stats_path = "result.csv"

    video_manager = VideoManager([video_path])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)

    scene_manager.add_detector(ContentDetector(threshold=threshold))
    video_manager.set_downscale_factor()

    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)

    # result
    with open(stats_path, "w") as f:
        stats_manager.save_to_csv(f)

    scene_list = scene_manager.get_scene_list()
    print(f"{len(scene_list)} scenes detected!")

    save_images(
        scene_list,
        video_manager,
        num_images=1,
        image_name_template="$SCENE_NUMBER",
        output_dir=f"scenes/{folder_name}",
    )

    write_scene_list_html("result.html", scene_list)

    info_list = list()
    for scene in scene_list:
        info = dict()
        start, end = scene
        info["start"] = start.get_seconds()
        info["end"] = end.get_seconds()
        info_list.append(info)

    return info_list


def load_scene_ocr_info(
    scene_paths: List[PosixPath],
) -> Union[List[List[Tuple[Any]]], List[int]]:
    """Use ocr on different scenes to get lyrics.

    Args:
        scene_paths (List[PosixPath]): func.video_preprocessing의 different_lyrics_detect에서 탐지된 장면들(jpg)이 저장된 파일 경로

    Returns:
        Union[List[List[Tuple[Any]]], List[int]]

    Examples:
        >>> scene_ocr_info_list, no_lyric_scene_idx_list = load_scene_ocr_info(scene_paths)
        >>> print(scene_ocr_info_list)
            [[([[105, 30], [635, 30], [635, 115], [105, 115]],
            'strawberry moon',
            0.5790058600266091),
            ([[309, 112], [431, 112], [431, 164], [309, 164]],
            '아이유',
            0.9998450753727066)], ...]
        >>> print(no_lyric_scene_idx_list)
            [0, 7, 30, 39, ...]
    """
    reader = easyocr.Reader(
        ["ko", "en"]
    )  # this needs to run only once to load the model into memory

    scene_ocr_info_list = list()
    no_lyric_scene_idx_list = list()

    for idx, scene in enumerate(scene_paths):
        ocr_results = reader.readtext(str(scene))
        scene_ocr = list()
        for ocr_result in ocr_results:
            # location, ocr_msg, prob = result
            # (x1, y1), (x2,y1), (x2, y2), (x1, y2) = location
            scene_ocr.append(ocr_result)

        if len(scene_ocr) == 0:  # 기본적으로 가사 데이터가 최소 1줄임
            no_lyric_scene_idx_list.append(idx)
            scene_ocr_info_list.append(scene_ocr)
            continue
        scene_ocr_info_list.append(scene_ocr)

    return scene_ocr_info_list, no_lyric_scene_idx_list


def get_ocr_list(scene_ocr_info_list: List[List[Tuple[Any]]]) -> List[List[str]]:
    """Get only ocr information from scene.

    Args:
        scene_ocr_info_list (List[List[Tuple[Any]]]): load_scene_ocr_info 함수의 리턴값
    Returns:
        List[List[str]]

    Examples:
        >>> print(get_ocr_list())
            [['strawberry moon', '아이유'],
            ['strawberry moon', '아이유', '달이 익어가니 서둘러 젊은 피야', '민들레 한 송이 들고'],...]

    """
    ocr_list = list()
    for scene_info in scene_ocr_info_list:
        scene_lyrics = [ocr_info[1] for ocr_info in scene_info]
        ocr_list.append(scene_lyrics)
    return list(map(lambda x: " ".join(x), ocr_list))


def get_total_scene_info(
    scene_time_info_list: List[Dict[str, float]],
    ocr_list: List[List[str]],
    song_info: Dict[str, str],
) -> List[Scene]:
    """Generate a list of Scene class objects.

    Args:
        scene_time_info_list (List[Dict[str, float]]): load_scene_time_info() 함수의 리턴값
        ocr_list (List[List[str]]): get_ocr_list() 함수의 리턴값
    Returns:
        Union[List[List[Tuple[Any]]], List[int]]

    Examples:
        >>> print(get_total_scene_info())
            [Scene(singer_name='아이유'
            song_name='strawberry moon',
            start=0.0, end=11.745078411745078,
            ocr_lyrics=None),...]
    """
    total_scene_info_list = list()
    for scene_time_info, ocr_lyrics in zip(scene_time_info_list, ocr_list):
        scene_dict = dict()
        scene_dict["start"] = scene_time_info["start"]
        scene_dict["end"] = scene_time_info["end"]
        scene_dict.update(song_info)
        scene_dict["ocr_lyrics"] = ocr_lyrics

        ocr_scene = Scene(**scene_dict)

        total_scene_info_list.append(ocr_scene)

    return total_scene_info_list
