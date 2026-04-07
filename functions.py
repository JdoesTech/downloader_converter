import yt_dlp
import os
import librosa
import numpy as np
import soundfile as sf

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
        
def add_noise_to_audio_randomly(input_file, output_file, noise_level):
    y, sr = librosa.load(input_file, sr=None)
    noise = np.random.randn(len(y)) * noise_level
    duration = len(y)
    noise_duration  = int(duration*0.09)
    start = np.random.randint(0, duration-noise_duration)
    end= start + noise_duration
    augmented_audio = y.copy()
    augmented_audio[start:end] += noise[start:end]
    
    sf.write(output_file, augmented_audio, sr)

def basic_noise_addition(filename, output_file):
    y, sr = librosa.load(filename, sr=None)
    noise =np.random.normal(0, 0.009, y.shape)
    y_noisy = y + noise
    sf.write(output_file, y_noisy, sr)
        

