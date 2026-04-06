import yt_dlp
import os

output_path = "./downloads"

def download_mp4(url, output_path):
    ydl_options ={
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
    }
    
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        ydl.download([url])
        
def download_mp3(url, output_path, convert_to_mp3=True):
    ydl_options ={
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "postprocessors": []
    }
    
    if convert_to_mp3:
        ydl_options["postprocessors"].append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        })
        
    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        ydl.download([url]) 
        

