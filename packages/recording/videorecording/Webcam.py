# webcam.py
import cv2

class Webcam:
    def __init__(self):
        self.cap = None
        self.fourcc = None
        self.video_width = None
        self.video_height = None

    def start(self):
        self.cap = cv2.VideoCapture(0)
        self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def start_video_writer(self, video_id):
        return cv2.VideoWriter(f'./.mp4/output_{video_id}.mp4', self.fourcc, 60.0, (self.video_width, self.video_height))

    def read(self):
        return self.cap.read()

    def is_opened(self):
        return self.cap.isOpened()

    def release(self):
        self.cap.release()
