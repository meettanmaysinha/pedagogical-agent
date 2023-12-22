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
            self.cap = cv2.VideoCapture(0)
            self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # def record(self):
        #     "Video starts being recorded"
        #     # counter = 1
        #     timer_start = time.time()
        #     timer_current = 0
        #     while self.is_opened():
        #         ret, video_frame = self.cap.read()
        #         if ret:
        #             self.out.write(video_frame)
        #             # print(str(counter) + " " + str(self.frame_counts) + " frames written " + str(timer_current))
        #             self.frame_counts += 1
        #             # counter += 1
        #             # timer_current = time.time() - timer_start
        #             time.sleep(1/self.fps)
        #             # gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
        #             # cv2.imshow('video_frame', gray)
        #             # cv2.waitKey(1)
        #         else:
        #             break


#########################################################################################################
                
        def record_video(self, interval = 5):
            start_time = time.time()
            video_id = 0
            out = self.write_video_file(video_id) # Save video clip

            while self.cap.is_opened():
                ret, frame = self.cap.read()
                out.write(frame)
                cv2.imshow('Webcam Feed', frame)

                # If video length longer than interval set, save video
                if time.time() - start_time > interval: 
                    out.release()
                    print(f"Run: {video_id}")

                    # self.hume_api.set_file_path(f"./.mp4/output_{video_id}.mp4") # Set video clip path for Hume API
                    # print(self.hume_api.get_file_path())

                    video_id += 1
                    start_time = time.time()

                    out = self.write_video_file(video_id) # Save video clip

                    # # Run Hume API in a separate thread
                    # thread = threading.Thread(target=self.hume_api.handle_hume_call, args=[video_id])
                    # thread.start()

                # Press 'q' to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            self.release()

#########################################################################################################
                

        def release(self):
            "Ends video recording and thread"
            self.cap.release()
            cv2.destroyAllWindows()

        def start(self):
            "Launches the video recording function using a thread"
            video_thread = threading.Thread(target=self.record_video)
            video_thread.start()

        def is_opened(self):
            return self.cap.isOpened()

        def write_video_file(self, video_id):
            "Saves the video clip to a file"
            return cv2.VideoWriter(f'./.mp4/output_{video_id}.mp4', self.fourcc, 60.0, (self.video_width, self.video_height)) 



    

    