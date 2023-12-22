#pip install opencv-python numpy pyaudio

from __future__ import print_function, division
from videorecording.video_recorder import VideoRecorder
from audiorecording.audio_recorder import AudioRecorder
import numpy as np
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os

import sys
sys.path.append('/path/')



class AVRecorder():
    def __init__(self):
        self.video_thread = VideoRecorder()
        self.audio_thread = AudioRecorder()


    def start_AVrecording(self):
        self.audio_thread.start()
        self.video_thread.start()

    def start_video_recording(self,filename="test"):
            self.video_thread.start()
            return filename
    
    def start_audio_recording(self,filename="test"):
        self.audio_thread.start()
        return filename

    def stop_AVrecording(self, filename="test"):
        self.audio_thread.stop() 
        frame_counts = self.video_thread.frame_counts
        elapsed_time = time.time() - self.video_thread.start_time
        recorded_fps = frame_counts / elapsed_time
        print("total frames " + str(frame_counts))
        print("elapsed time " + str(elapsed_time))
        print("recorded fps " + str(recorded_fps))
        self.video_thread.stop() 

        # Makes sure the threads have finished
        while threading.active_count() > 1:
            time.sleep(1)

        # Merging audio and video signal
        if abs(recorded_fps - 6) >= 0.01:    # If the fps rate was higher/lower than expected, re-encode it to the expected
            print("Re-encoding")
            cmd = "ffmpeg -r " + str(recorded_fps) + " -i temp_video.avi -pix_fmt yuv420p -r 6 temp_video2.avi"
            subprocess.call(cmd, shell=True)
            print("Muxing")
            cmd = "ffmpeg -y -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video2.avi -pix_fmt yuv420p " + filename + ".avi"
            subprocess.call(cmd, shell=True)
        else:
            print("Normal recording\nMuxing")
            cmd = "ffmpeg -y -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video.avi -pix_fmt yuv420p " + filename + ".avi"
            subprocess.call(cmd, shell=True)
            print("..")

    def file_manager(self, filename="test"):
        "Required and wanted processing of final files"
        local_path = os.getcwd()
        if os.path.exists(str(local_path) + "/temp_audio.wav"):
            os.remove(str(local_path) + "/temp_audio.wav")
        if os.path.exists(str(local_path) + "/temp_video.avi"):
            os.remove(str(local_path) + "/temp_video.avi")
        if os.path.exists(str(local_path) + "/temp_video2.avi"):
            os.remove(str(local_path) + "/temp_video2.avi")
        # if os.path.exists(str(local_path) + "/" + filename + ".avi"):
        #     os.remove(str(local_path) + "/" + filename + ".avi")
            
    def runmain(self):
        self.start_AVrecording()
        time.sleep(5)
        self.stop_AVrecording()
        self.file_manager()