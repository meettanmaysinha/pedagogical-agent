# webcam.py
import cv2
import os

class Webcam:
    def __init__(self, recording_folder="recordings"):
        self.cap = None
        self.fourcc = None
        self.fps = None
        self.video_width = None
        self.video_height = None
        self.recording_folder = recording_folder

    def start(self, fps=20.0):
        self.cap = cv2.VideoCapture(1)
        self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.fps = fps
        self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print("Video started")

    def write_video_file(self, video_name):
        # Create directory if it does not exist
        video_directory = f"./{self.recording_folder}/video/"
        os.makedirs(video_directory, exist_ok=True)
        # return cv2.VideoWriter(video_directory + f'output_{video_id}.mp4', self.fourcc, 60.0, (self.video_width, self.video_height)) 
        print("Recording new video " + video_name)
        return cv2.VideoWriter(f'{video_directory + video_name}.mp4', self.fourcc, self.fps, (self.video_width, self.video_height))

    def read(self):
        return self.cap.read()

    def is_opened(self):
        return self.cap.isOpened()

    def release(self):
        self.cap.release()
