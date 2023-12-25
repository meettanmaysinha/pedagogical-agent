#pip install opencv-python numpy pyaudio

from __future__ import print_function, division
import numpy as np
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os

class AudioRecorder():
        "Audio class based on pyAudio and Wave"
        def __init__(self, rate = 44100, fpb = 1024, channels = 2):
            self.open = True
            self.rate = rate
            self.frames_per_buffer = fpb
            self.channels = channels
            self.format = pyaudio.paInt16
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(format=self.format,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer = self.frames_per_buffer)
            self.audio_frames = []

        def record(self, audio_file_name = "test"):
            "Audio starts being recorded"
            
            while self.open:
                data = self.stream.read(self.frames_per_buffer) 
                self.audio_frames.append(data)
                if not self.open:
                    break
            self.stop(audio_file_name)
####
            
        def stop(self, audio_file_name = "test"):
            "Finishes the audio recording therefore the thread too"
            if self.open:
                self.open = False
                self.stream.stop_stream()
                self.stream.close()
                self.audio.terminate()
                self.write_audio_file(audio_file_name)
                

        def start(self):
            "Launches the audio recording function using a thread"
            audio_thread = threading.Thread(target=self.record)
            audio_thread.start()
        
        def write_audio_file(self, audio_file_name = "test"):
            audio_file = wave.open(f'../../audio/{audio_file_name}.wav', 'wb')
            audio_file.setnchannels(self.channels)
            audio_file.setsampwidth(self.audio.get_sample_size(self.format))
            audio_file.setframerate(self.rate)
            audio_file.writeframes(b''.join(self.audio_frames))
            audio_file.close()
            