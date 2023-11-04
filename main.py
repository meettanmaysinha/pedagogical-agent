# main.py
import asyncio
from classes.video_processor import VideoProcessor
import apikey

API_KEY = apikey.API_KEY

def main():
    loop = asyncio.get_event_loop()
    video_processor = VideoProcessor(API_KEY)
    video_processor.start_webcam()
    loop.run_until_complete(video_processor.process_video())

if __name__ == "__main__":
    main()
