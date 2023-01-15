from pydantic import BaseModel


class Scene(BaseModel):
    singer_name: str
    song_name: str
    start: float
    end: float
    ocr_lyrics: str = None
    corrected_lyrics: str = None
