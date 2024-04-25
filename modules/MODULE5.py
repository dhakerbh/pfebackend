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
    OUTPUT_TEXT = Path(__file__).resolve().parent.joinpath('data',f'{file_name}.txt')
    SUMMARY = Path(__file__).resolve().parent.joinpath('data',f'{file_name}_SUM.txt')

    if os.path.exists(SUMMARY):
        with open(f'modules/data/{file_name}_SUM.txt') as f:
            lines = f.readlines()
        return lines 
    elif os.path.exists(OUTPUT_TEXT):
        summary = summarize_text(transcript)
        return summary
    if( os.path.exists(OUTPUT_AUDIO)):
        print('MP3 file found , Skipping to transcripting')
    else:
        download_youtube_video(YOUTUBE_VIDEO_URL, OUTPUT_AUDIO)
    transcript = model.transcribe(OUTPUT_AUDIO.as_posix())
    transcript = transcript['text']
    open(OUTPUT_TEXT,'w').write(transcript)
    summary = summarize_text(transcript)
    open(SUMMARY,"w").write(summary)
    summary = open(SUMMARY,"r").readlines()
    print(type (summary) , summary)
    return summary
