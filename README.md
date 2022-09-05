# music-data-pipeline

구상하고 있는 전체 파이프라인을 pseudo-code로 표현하면 다음과 같습니다.



# 1번째 파이프라인

```python
def make_TTS_training_data():
    download_mp4_from_Youtube() #가사가 보이는 유튜브 동영상 다운로드
    crop_video() # 가사 부분만 crop
    generate_scenes_using_scenedetector() #scenedetector를 이용하여 가사 변하는 부분을 jpg 파일로 저장
    generate_lyrics_using_OCR() #OCR을 이용해서 가사 변환
    #crawling_all_lyrics() #가수와 제목정보를 이용하여 가사를 인터넷에서 긁어옴
    #compare_lyrics() #크롤링한 가사와 OCR 가사를 비교해서 비슷한 가사로 변환
    #voice_isolation() #적절한 가사들에 대해 MR제거한 목소리 변환
    #save_TTS_training_data()

def voice_synthesis():
    load_TTS_training_data()
    train_TTS()

if __name__ == '__main__':
    make_TTS_training_data()
    voice_synthesis()
```

# 2번째 파이프라인 -> STT 성능이 좋지 않아 보류

```python
def make_TTS_training_data():
    download_mp3_from_Youtube() #유튜브에서 원하는 비디오를 mp3파일 형태로 변환
    mp3_files_to_wav_files() #mp3 파일들을 wav 파일로 변환
    voice_isolation_for_wav_files() #wav 파일들에 대해 spleeter를 적용하여 MR제거된 목소리 추출
    nonsilence_segmentation_on_isolated_vocal() #MR제거된 목소리 데이터들을 작은 단위로 segmentation
    STT_on_nonsilence_segmentation() #작은 단위의 MR제거된 목소리 데이터에 대해 STT

def voice_synthesis():
    load_TTS_training_data()
    train_TTS()

if __name__ == '__main__':
    make_TTS_training_data()
    voice_synthesis()
```

* TODO
    * Requirements
        * OCR requirements
            * pip install scenedetect[opencv] --upgrade
            * pip install --trusted-host pypi.python.org moviepy
            * !pip install imageio-ffmpeg
            * !pip install easyocr
        * STT requirements
            * sudo apt-get install ffmpeg
            * pip3 install pydub
        
    * Test code 작성
    * import os -> from pathlib import Path로 수정
    * makedir 수정(downloader에서 문제 발생)
