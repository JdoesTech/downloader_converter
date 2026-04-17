import yt_dlp
import os
from pathlib import Path
import zipfile
import librosa
import numpy as np
import soundfile as sf
import noisereduce as nr
import pypandoc
import gzip

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
    freqs= np.fft.rfftfreq(n, 1/sample_rate)
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
    
    sf.write(output_file, cleaned, sample_rate)
    print(f"Cleaning is complete. File has been saved as {output_file}")
    
supported_formats= {
    "input": ["docx", "pdf", "md", "markdown", "txt", "html", "odt", "rst", "latex", "epub"],
    "output": ["docx", "pdf", "md", "markdown", "txt", "html", "odt", "rst", "latex", "epub"],
}

def convert_document(input_path, input_format, output_format,output_path):
    try:
        if input_format not in supported_formats["input"]:
            return {"status": "error", "message": f"Unsupported input format: {input_format}"}
        if output_format not in supported_formats["output"]:
            return {"status": "error", "message": f"Unsupported output format: {output_format}"}
        
        input_path = Path(input_path)
        if not input_path.exists():
            return {"status": "error", "message": f"File not found: {input_path}"}
        
        file_extension = input_path.suffix.lower().lstrip(".")
        selected_input= input_format.lower()
        
        if file_extension != selected_input:
            return{
                "status": "error",
                "message": f"File extension {file_extension} does not match selected input format {selected_input}"
                            f"Please ensure the file extension matches the selected input format."
            }
            
        if selected_input == "docx" and file_extension=="docx":
            try:
                with zipfile.ZipFile(input_path, "r") as d:
                    if "word/document.xml" not in d.namelist():
                        return {"status": "error", "message": "Invalid DOCX file: missing document.xml"}
            except Exception:
                pass
            
        if output_path is None:
            output_path = input_path.with_suffix(f".{output_format.lower()}")
        else:
            output_path = Path(output_path)
            
        pypandoc.convert_file(
            str(input_path),
            output_path.lower(),
            outputfile=str(output_path),
            format=input_format.lower()
        )
        
        return {
            "status": "success",
            "message": f"File converted successfully: {output_path}",
            "output_path": str(output_path)
        }
        
    except Exception as e:
        return{
            "status": "error",
            "message": f"An error occurred during conversion: {str(e)}"
        }
            

def compress_text_file(input_file, output_file):
    try:
        with open(input_file, "rb") as f_in:
            with gzip.open(output_file, "wb") as f_out:
                f_out.writelines(f_in)
        print(f"File compressed successfully: {output_file}")
        
    except Exception as e:
        print(f"An error occurred during compression: {str(e)}")
        
