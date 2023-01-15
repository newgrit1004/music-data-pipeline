# music-data-pipeline

본 레포에서 구현하고 있는 기능은 다음과 같습니다.

- 유튜브 비디오 또는 플레이리스트로부터 영상 다운로드 받기
- 다운로드 받은 영상(.mp4)을 mp3 파일 또는 wav 파일로 변환하기
- 다운로드 받은 영상의 길이를 편집하거나, 특정 좌표를 제공하여 특정 좌표만큼의 보이는 비디오로 잘라내기
- 주어진 비디오를 gray-scale 비디오로 변환하기
- spleeter를 이용하여 주어진 음원에 대한 vocal isolation 진행하기
- 사람의 음성이 포함된 음원에서 침묵/비침묵 구간을 시간대별로 태그하며, 해당 시간대별로 주어진 음성을 segmentation해서 저장하기
- 가수와 노래제목을 제공하면 멜론 크롤러 클래스를 이용하여 해당 노래의 가사를 OCR를 이용하여 추출하기

본 레포에서 구현해야하는 추가 기능은 다음과 같습니다.
- OCR로 추출한 가사와 크롤링을 이용하여 추출한 가사를 비교하여 크롤링으로 추출한 가사로 자동 변경하기
- 정확한 가사와 PySceneDetect를 이용한 Scene 데이터, 그리고 spleeter를 이용하여 다량의 짧은 길이 Speech AI 학습 데이터를 생성하기
- KSS 데이터로 pre-trained된 모델을 생성하고, 본 레포에서 제안하는 데이터로 이어서 학습을 진행한 뒤, 가수의 음색이 드러나는 목소리가 나오는지 체크하기


구상하고 있는 전체 파이프라인을 pseudo-code로 표현하면 다음과 같습니다.

# 1번째 파이프라인(본 레포 제안 방식)

```python
def make_TTS_training_data():
    download_mp4_from_Youtube() #가사가 보이는 유튜브 동영상 다운로드
    crop_video() # 가사 부분만 crop
    generate_scenes_using_scenedetector() #scenedetector를 이용하여 가사 변하는 부분을 jpg 파일로 저장
    generate_lyrics_using_OCR() #OCR을 이용해서 가사 변환
    crawling_all_lyrics() #가수와 제목정보를 이용하여 가사를 인터넷에서 긁어옴
    #compare_lyrics() #크롤링한 가사와 OCR 가사를 비교해서 비슷한 가사로 변환
    #voice_isolation() #적절한 가사들에 대해 MR제거한 목소리 변환
    #save_TTS_training_data()

# def voice_synthesis():
#     load_TTS_training_data()
#     train_TTS()

if __name__ == '__main__':
    make_TTS_training_data()
    # voice_synthesis()
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
    * Requirements 정리 필요 -> STT 모듈은 이제 안쓰는게 많음
        * OCR requirements
            * pip install scenedetect[opencv] --upgrade
            * pip install --trusted-host pypi.python.org moviepy
            * !pip install imageio-ffmpeg
            * !pip install easyocr
        * STT requirements
            * sudo apt-get install ffmpeg
            * pip3 install pydub
    * 계획
        * quick_start.ipynb에서의 작업을 마무리하여 Scene Object가 최대한 정확한 가사를 가지도록 맞춘다.
        * spleeter와 Scene Object에서의 start, end 시간을 이용하여 한국어 가사와 wav 파일을 매칭시키며, 이는 추후에 Speech AI의 학습 데이터로 사용된다.
        * 사용할 Speech AI 모델을 검토하며, 해당 Speech AI에서 트레이닝할 수 있는 데이터 포맷에 맞게 상단의 데이터를 정리한다.
        * KSS 데이터셋과 같은 데이터로 pre-trained 모델을 먼저 얻은 뒤, 위의 작업을 통해 얻은 데이터셋을 이용하여 이어서 학습한다.
        * pre-trained 모델에서 새로운 데이터셋으로 모델을 학습할 때, 학습 초반의 모델을 best_model로 선정한다.
            * 이유는 사람의 발성 중, 발음은 대부분 비슷하며 초반에 가장 많이 바뀌는 부분은 음색이다.
            * KSS 데이터셋은 정확한 텍스트로 학습되었지만, 본 레포에서 제안하는 방식은 부정확한 데이터(e.g. OCR lyric이 이상하다, scene이 제대로 안나뉘어있다, voice isolation이 원하는 수준만큼 안됐다 등)로 학습을 진행하게 되므로, 학습 초반에 음색이 많이 바뀔 때 그 점만을 이용하는 것이 본 레포의 아이디어이다.




# 주피터 노트북 파일 설명
- songdownloader_test_code.ipynb
    - utils.downloader의 YoutubeSongDownloader 기능 주피터 노트북 테스트 코드
- spleeter_test.ipynb
    - utils.downloader의 PlaylistDownloader를 통해 유튜브 플레이리스트에 들어있는 동영상들을 다운로드 받는다.
    - 다운로드 받은 동영상의 확장자를 mp4 -> mp3 -> wav로 변환한다.
    - vocal isolation이 가능한 spleeter 라이브러리를 사용하여 플레이리스트에 들어있는 가수 목소리를 추출한다.
- silience_test.ipynb
    - wav 파일이 존재할 경우, 주어진 wav 파일에서 침묵 구간/비침묵 구간을 millisecond 단위로 나누며 태그해주는 함수(func.audio_preprocessing의 get_time_segments 함수) 주피터 노트북 테스트 코드
    - 또한, 비침묵 구간에 해당하는 구간만 wav 파일로 잘라내어 저장하는 것도 가능
- crawling_test.ipynb
    - utils.crawler의 MelonCrawler를 사용하여 가수의 이름과 가사를 알고 싶은 노래의 제목을 입력으로 주면, 크롤링을 통해 원하는 노래의 가사를 읽어온다.
    - 가사를 얻고자 하는 노래 리스트를 만들어서 반복문을 돌리면 여러 노래에 대한 가사를 크롤링할 수 있다.
    - 하지만, 한 번에 많은 노래를 크롤링할 경우 IP Block을 당할 수 있으므로 노래 리스트를 나누고, 천천히 크롤링하는 것을 추천한다.
    - IP Block이 되었는지 체크하는 방법은 웹브라우저를 통해 멜론 아티스트 곡정보 웹페이지로 직접 들어갔을 때, 하단의 인덱스로 다른 곡 페이지 이동이 불가능하다면 IP Block이 되었다고 볼 수 있다.
    - 크롤링 결과 파일을 직접 공유하기보다는 주피터 노트북 출력 결과 예시만 보여주는 것으로 설정

- PySceneDetect_test.ipynb
    - file/yaml/song_url.yml에 담겨있는 비디오를 모두 다운로드 받는다.
    - 다운로드 받은 비디오를 gray_scale로 전환하며, 그 이유는 OCR이 grayscale에서 더 잘 동작하기 때문이다.
    - Color Coded Lyrics를 만드는 유튜버마다 가사 노출 방식 및 한국어 가사 좌표 정보가 다르기 때문에, 좌표 및 PySceneDetect threshold를 수동으로 작업해서 Scene이 최대한 누락되지 않고, 모든 가사가 잘 나오도록 설정한다.(이 작업을 setting_threshold.ipynb에서 주로 했었음)


# 미완성 파일 및 개발용으로만 사용했던 파일
- setting_threshold.ipynb(To be developed)
    - Color Coded Lyrics 마다 가사 노출 방법(e.g. 가사가 서서히 사라지는 느낌, 가사가 바로 변하는 느낌 등)이 다르기 때문에 이에 따른 PySceneDetect Threshold를 계산하기 위해 사용했던 주피터 노트북

- gray_cropped_video_to_wav.ipynb(To be developed)
    - gray_cropped_video(Color Coded Lyrics 형식의 비디오에서 한국어 가사에 해당되는 부분만 잘라낸 뒤, gray_scale 처리한 비디오)에 들어있는 영상을 wav file로 변환한다.
    - scene_object_dict이라는 pickle 파일을 읽어와서 Scene 별로 담긴 해당 가사가 보이는 시작시간/끝시간/OCR로 검출된 가사 정보를 본다.
    - OCR로 검출된 가사의 길이가 너무 짧거나, 제대로 된 한국어가 아닌 경우 배제하는 전처리를 진행한다.


- quick_start.ipynb(To DO)
    - 상단에서 여러 개의 주피터 노트북 작업 등을 통해 정리한 데이터들을 pickle 파일로 저장해두었다.
    - quick_start.ipynb에서는 pickle 파일을 바로 load하여 OCR로 검출된 부정확한 가사와 크롤링으로 가져온 정확한 가사를 자동으로 일치화시키는 작업을 진행한다.(Not Finished)
    - 정확한 가사와 OCR 가사를 최대한 일치시키며 맞춤법 검사 등을 통해 부정확한 가사가 없도록 설정한다
