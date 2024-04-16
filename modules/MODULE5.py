##YOUTUBE VIDEO SUMMARIZERR 
import os
import whisper
from pytube import YouTube
from pathlib import Path
from MODULE3 import summarize_text
WHISPER_MODEL = 'base'
model = whisper.load_model(WHISPER_MODEL)

def download_youtube_video(url, output_audio):
    # youtube video object
    youtube_video = YouTube(url)
    stream = youtube_video.streams.filter(only_audio=True).first()    
    stream.download(filename=output_audio)

def summarize_video(url):
    url = str(url)
    file_name = url[url.find("?v=")+3: url.find("?v=")+14]
    YOUTUBE_VIDEO_URL = url
    OUTPUT_AUDIO = Path(__file__).resolve().parent.joinpath('data',f'{file_name}.mp3')
    if os.path.exists(OUTPUT_AUDIO):
        with open(f'data/{file_name}.txt') as f:
            lines = f.readlines()
            
        return lines 

    download_youtube_video(YOUTUBE_VIDEO_URL, OUTPUT_AUDIO)
    transcript = model.transcribe(OUTPUT_AUDIO.as_posix())
    transcript = transcript['text']
    summary = summarize_text(transcript)
    with open(f'data/{file_name}.txt',"w") as f:
        f.write(summary)
    f.close()
    return summary
