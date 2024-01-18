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
        def __init__(self, rate = 44100, fpb = 2048, device_index = 0):
            self.open = True
            self.rate = rate
            self.frames_per_buffer = fpb
            self.format = pyaudio.paInt16
            self.audio = pyaudio.PyAudio()
            self.device_index = device_index
            # self.max_input_channels = self.get_max_input_channels() # Get max input channels
            self.max_input_channels = 1 # Mono recording
            self.stream = self.audio.open(format=self.format,
                                        channels=self.max_input_channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer = self.frames_per_buffer)
            self.audio_frames = []
            
        
        def get_max_input_channels(self):
            info = self.audio.get_device_info_by_index(self.device_index)
            return info['maxInputChannels']
        
        def record(self, audio_file_name = "test"):
            "Audio starts being recorded"
            print("AUDIO RECORDING", self.open)
            while self.open:
                data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False) 
                self.audio_frames.append(data)
                if not self.open:
                    break
            self.stop(audio_file_name)
####
            
        def stop(self, audio_file_name = "test"):
            "Finishes the audio recording therefore the thread too"
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
            # Create directory if it does not exist
            
            audio_directory = './output/audio/'
            os.makedirs(audio_directory, exist_ok=True)
            
            # print("Audio saving in progress...", audio_directory)
            # Save audio file
            audio_file = wave.open(audio_directory + f'{audio_file_name}.wav', 'w')
            audio_file.setnchannels(self.max_input_channels)
            audio_file.setsampwidth(self.audio.get_sample_size(self.format))
            audio_file.setframerate(self.rate)
            audio_file.writeframes(b''.join(self.audio_frames))
            audio_file.close()

            #Reset audio frames for new clip
            self.audio_frames = []
            # print("Audio saved" + audio_file_name)
            