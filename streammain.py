# main.py
import asyncio
from VideoProcessor import VideoProcessor
from packages.emotionpattern.PatternMine import PatternMine
import apikey
import time
import batchuploader

API_KEY = apikey.API_KEY

def main():
    video_processor = VideoProcessor(API_KEY, interval=5, recording_folder="recordings") # Intervals can be updated for short/long term analysis
    seq_pattern_mine = PatternMine("PrefixSpan") 
    high_util_pattern_mine = PatternMine("Two-Phase")
    
    
    loop = asyncio.get_event_loop()
    video_processor.start_webcam()
    loop.run_until_complete(video_processor.process_video())

    time.sleep(5) # Delay to allow async tasks to clear
    print("Running Pattern Mining Algorithms...")
    # Sequential Pattern mining (Arguments: min_sup, min_pat)
    seq_pattern_mine.run("./results/extracted_sequence.txt", "./results/output_sequence.txt", 0.5, 5)
    # High Utility Pattern mining (Arguments: min_utility)
    high_util_pattern_mine.run("./results/extracted_utility.txt", "./results/output_utility.txt", 1)

if __name__ == "__main__":
    main()