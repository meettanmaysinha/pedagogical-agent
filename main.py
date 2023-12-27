# main.py
import asyncio
from VideoProcessor import VideoProcessor
from packages.emotionpattern.PatternMine import PatternMine
import apikey
import time

API_KEY = apikey.API_KEY

def main():
    video_processor = VideoProcessor(API_KEY, interval=5) # Intervals can be updated for short/long term analysis
    pattern_mine = PatternMine("PrefixSpan",0.5,5) 
    
    
    loop = asyncio.get_event_loop()
    video_processor.start_webcam()
    loop.run_until_complete(video_processor.process_video())

    print("Running Sequence Mining Algorithm...")
    time.sleep(5) # Delay to allow async tasks to clear
    pattern_mine.run("extracted_sequence.txt", "output_sequence.txt")

if __name__ == "__main__":
    main()
