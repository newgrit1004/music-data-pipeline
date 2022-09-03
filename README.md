## music-data-pipeline

구상하고 있는 전체 파이프라인을 pseudo-code로 표현하면 다음과 같습니다.

```python
download_mp3_from_Youtube() #유튜브에서 원하는 비디오를 mp3파일 형태로 변환
mp3_files_to_wav_files() #mp3 파일들을 wav 파일로 변환
voice_isolation_for_wav_files() #wav 파일들에 대해 spleeter를 적용하여 MR제거된 목소리 추출
nonsilence_segmentation_on_isolated_vocal() #MR제거된 목소리 데이터들을 작은 단위로 segmentation
STT_on_nonsilence_segmentation() #작은 단위의 MR제거된 목소리 데이터에 대해 STT
```

* TODO
    * Requirements
        * sudo apt-get install ffmpeg
        * pip3 install pydub
    * Test code 작성
