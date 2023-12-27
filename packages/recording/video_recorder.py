from __future__ import print_function, division
import numpy as np
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os

class VideoRecorder():  
        "Video class based on openCV"
        def __init__(self, fps=60):
            self.start_time = time.time()
            self.cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
            self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


#########################################################################################################
                
        def record_video(self, video_name = "test"):
            print("RECORDING VIDEO", self.cap.isOpened())
            out = self.write_video_file(video_name) # Create video clip

            while self.cap.isOpened():
                ret, frame = self.cap.read()
                out.write(frame)
                if ret == True: 
                    cv2.imshow('Webcam Feed', frame)
                print("IMSHOW Frames")

            out.release() # Save video clip
            self.release() # Close webcam


#########################################################################################################
                

        def release(self):
            "Ends video recording and thread"
            self.cap.release()
            cv2.destroyAllWindows()

        def start(self):
            "Launches the video recording function using a thread"
            print("Video recording in progress...")
            video_thread = threading.Thread(target=self.record_video)
            video_thread.start()

        def write_video_file(self, video_name = "test"):
            "Saves the video clip to a file"
            
            # Create directory if it does not exist
            video_directory = "./output/video/"
            os.makedirs(video_directory, exist_ok=True)
            return cv2.VideoWriter(video_directory + f'{video_name}.mp4', self.fourcc, 60.0, (self.video_width, self.video_height)) 