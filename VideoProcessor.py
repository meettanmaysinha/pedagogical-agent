# video_processor.py

import cv2
import time
import threading
import asyncio
from packages.hume.Hume import HumeAPI
from packages.recording.AVRecorder import AVRecorder
from packages.recording.Webcam import Webcam

class VideoProcessor:
    def __init__(self, api_key, file_path="../output_0", interval=5):
        self.hume_api = HumeAPI(api_key, file_path) # Create instane of HumeAPI
        # self.webcam = AVRecorder() # Create instance of AVRecorder
        self.webcam = Webcam() # Create instance of Webcam
        self.interval = interval

    def start_webcam(self):
        # self.webcam.start_AVrecording() # Start webcam
        self.webcam.start()

    async def process_video(self):
        start_time = time.time()
        # self.webcam.start_AVrecording() # Start webcam
        av_id = 0
        av_name = f"output_{av_id}"
        # out = self.webcam.save_AVrecording(video_name) # Save video clip
        out = self.webcam.write_video_file(av_name)

        while self.webcam.is_opened:
            ret, frame = self.webcam.read()
            out.write(frame)
            cv2.imshow('Webcam Feed', frame)

            # If video length longer than interval set, save video
            if time.time() - start_time > self.interval: 
                # out.release()
                print(f"Run: {av_name}")

                # Set AV clip path for Hume API
                self.hume_api.set_file_path(f"./.mp4/{av_name}.mp4") 
                print(self.hume_api.get_file_path())

                # Save AV clip 
                # self.webcam.save_AVrecording(av_name)
                
                # Set new av ID and name for next clip
                av_id += 1
                av_name = f"output_{av_id}"
                start_time = time.time()

                # out = self.webcam.write_video_file(video_name) # Save video clip

                # Run Hume API in a separate thread
                thread = threading.Thread(target=self.hume_api.handle_hume_call, args=[av_id])
                thread.start()

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # self.webcam.stop_AVrecording()
        self.webcam.release()
        cv2.destroyAllWindows()
