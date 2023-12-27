#pip install opencv-python numpy pyaudio

from __future__ import print_function, division
from packages.recording import audio_recorder,video_recorder
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os



class AVRecorder():
    def __init__(self):
        self.video_thread = video_recorder.VideoRecorder()
        self.audio_thread = audio_recorder.AudioRecorder()
        self.open = True

    def start_video_recording(self):
        self.video_thread.start()
    
    def save_video_recording(self,filename="test"):
        self.video_thread.write_video_file(filename)
         
    def start_audio_recording(self):
        self.audio_thread.start()

    def save_audio_recording(self,filename="test"):
        self.audio_thread.write_audio_file(filename)

    def start_AVrecording(self):
        print("Start AV Recording...")
        self.video_thread.start()
        self.audio_thread.start()

    def save_AVrecording(self,filename="test"):
        print("Trying to save AV....")
        self.save_audio_recording(filename)
        self.save_video_recording(filename)
        av_file_path = "./output/av_output/"
        # Merging audio and video signal
        # if abs(recorded_fps - 6) >= 0.01:    # If the fps rate was higher/lower than expected, re-encode it to the expected
        #     print("Re-encoding")
        #     cmd = "ffmpeg -r " + str(recorded_fps) + " -i {temp_video}.avi -pix_fmt yuv420p -r 6 {temp_video2}.avi"
        #     subprocess.call(cmd, shell=True)
        #     print("Muxing")
        #     cmd = "ffmpeg -y -ac 2 -channel_layout stereo -i {temp_audio}.wav -i {temp_video2}.avi -pix_fmt yuv420p " + filename + ".avi"
        #     subprocess.call(cmd, shell=True)
        # else:
        print("Normal recording\nMuxing")
        cmd = f"ffmpeg -y -ac 2 -channel_layout stereo -i {filename}.wav -i {filename}.avi -pix_fmt yuv420p {av_file_path + filename}.avi"
        subprocess.call(cmd, shell=True)
        print("..")

    def stop_AVrecording(self, filename="test"):
        self.save_AVrecording(filename)
        self.audio_thread.stop(filename)
        self.video_thread.release()

        # Makes sure the threads have finished
        while threading.active_count() > 1:
            time.sleep(1)

        self.open = False
    
    def read(self):
        return self.video_thread.cap.read()
    # def file_manager(self, filename="test"):
    #     "Required and wanted processing of final files"
    #     local_path = os.getcwd()
    #     if os.path.exists(str(local_path) + "/temp_audio.wav"):
    #         os.remove(str(local_path) + "/temp_audio.wav")
    #     if os.path.exists(str(local_path) + "/temp_video.avi"):
    #         os.remove(str(local_path) + "/temp_video.avi")
    #     if os.path.exists(str(local_path) + "/temp_video2.avi"):
    #         os.remove(str(local_path) + "/temp_video2.avi")
    #     # if os.path.exists(str(local_path) + "/" + filename + ".avi"):
    #     #     os.remove(str(local_path) + "/" + filename + ".avi")
            
    # def run_main(self):
    #     self.start_AVrecording()
    #     time.sleep(5)
    #     self.stop_AVrecording()
    #     self.file_manager()