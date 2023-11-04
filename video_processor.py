# video_processor.py
import cv2
import time
import threading
import asyncio
from hume_api import HumeAPI
from webcam import Webcam

class VideoProcessor:
    def __init__(self, api_key, file_path="../output_0"):
        self.hume_api = HumeAPI(api_key, file_path)
        self.webcam = Webcam()

    def start_webcam(self):
        self.webcam.start()

    async def process_video(self):
        start_time = time.time()
        video_id = 0
        out = self.webcam.start_video_writer(video_id)

        while self.webcam.is_opened():
            ret, frame = self.webcam.read()
            out.write(frame)
            cv2.imshow('Webcam Feed', frame)

            if time.time() - start_time > 5:
                out.release()
                print(f"Run: {video_id}")

                self.hume_api.set_file_path(f"./.mp4/output_{video_id}.mp4")
                print(self.hume_api.get_file_path())

                video_id += 1
                start_time = time.time()

                out = self.webcam.start_video_writer(video_id)

                thread = threading.Thread(target=self.hume_api.handle_hume_call)
                thread.start()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.webcam.release()
        cv2.destroyAllWindows()
