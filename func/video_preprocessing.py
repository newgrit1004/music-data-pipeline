from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import moviepy.editor as mp
from typing import Tuple
from pathlib import Path
import easyocr
from scenedetect import VideoManager, SceneManager, StatsManager
from scenedetect.detectors import ContentDetector
from scenedetect.scene_manager import save_images, write_scene_list_html

def trim_video(source_video_path:str, start_time:float, end_time:float, trimmed_video_path:str):
    """Trim the video and generate trimmed video using start_time and end_time.

    Args:
        source_video_path (str): the path of the source video file you want to trim.
        start_time (float): start time(second) to cut from the source video.
        end_time (float): end time(second) to cut from the source video.
        trimmed_video_path (str): the path of trimmed video.
    """
    ffmpeg_extract_subclip(source_video_path, start_time, end_time, targetname=trimmed_video_path)

def crop_video(source_video_path:str, coordinates:Tuple[int], cropped_video_path:str):
    """Crop the video and generate cropped video using resize_shape.

    Args:
        source_video_path (str): the path of the source video file you want to crop.
        coordinates (Tuple[int]): coordinates(x1, y1, x2, y2) to crop
        cropped_video_path (str): the path of cropped video.
    """
    x1, y1, x2, y2 = coordinates
    clip_resized = mp.VideoFileClip(source_video_path).crop(x1=x1, y1=y1, x2=x2, y2=y2)
    clip_resized.write_videofile(cropped_video_path)




def different_lyrics_detect(video_path:str, threshold:float):
    """Detect the scenes that have different lyrics from the cropped video and save them on ./scene folder.

    Args:
        video_path (str): a cropped video file path
        threshold (float): a threshold value of scene detector

    TODO:
        * determine what to return
    """
    stats_path = 'result.csv'

    video_manager = VideoManager([video_path])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)

    scene_manager.add_detector(ContentDetector(threshold=threshold))
    video_manager.set_downscale_factor()

    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)

    # result
    with open(stats_path, 'w') as f:
        stats_manager.save_to_csv(f, video_manager.get_base_timecode())

    scene_list = scene_manager.get_scene_list()
    print(f'{len(scene_list)} scenes detected!')

    save_images(
        scene_list,
        video_manager,
        num_images=1,
        image_name_template='$SCENE_NUMBER',
        output_dir='scenes')

    write_scene_list_html('result.html', scene_list)

    info_list = list()
    for scene in scene_list:
        info = dict()
        start, end = scene
        info['start'] = start.get_seconds()
        info['end'] = end.get_seconds()
        info_list.append(info)
