import yt_dlp
import os
import librosa
import numpy as np
import soundfile as sf
import noisereduce as nr

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
    
def noise_reduction_stationary(input_file, output_file):
    audio_data, sample_rate = librosa.load(input_file, sr=None)
    reduced_noise = nr.reduce_noise(
        y=audio_data,
        sr=sample_rate,
        prop_decrease=0.8,
        stationary=True
    )
    
    sf.write(output_file, reduced_noise, sample_rate)
    
def noise_reduction_non_stat(input_file, output_file):
    audio_data, sample_rate = librosa.load(input_file, sr=None, mono=True)
    n =len(audio_data)
    freqs= np.fft.rfftfreq(n, 1/sr)
    mags= np.abs(np.fft.rfft(audio_data))
    peak_idx= np.argmax(mags[1:])+1
    dominant_freq= freqs[peak_idx]
    noise_db = 20* np.log10(mags[peak_idx] / np.sqrt(n)+ 1e-10)
    
    print(f"Dominant Frequency: {dominant_freq:.1f} Hz at {noise_db:.1f} dB (global noise estimate)")
    
    cleaned= nr.reduce_noise(
        y=audio_data,
        sr=sample_rate,
        prop_decrease=0.8,
        stationary=False,
        n_std_thresh=1.5
    )
    
    sf.write(output_file, cleaned, sr)
    print(f"Cleaning is complete. File has been saved as {output_file}")