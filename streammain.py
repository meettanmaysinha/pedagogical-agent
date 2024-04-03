# main.py
import asyncio
from VideoProcessor import VideoProcessor
from packages.emotionpattern.PatternMine import PatternMine
import time
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("HUME_API_KEY")

def main():
    # Video Streaming Processor
    '''
    Parameters
    ----------
    api_key: str
        API Key for HumeAI
    
    interval - Currently deactivated: int
        Interval for recording (default = 5) 
    
    recording_folder: str
        Name of folder for recorded Audio and Video files used for HumeAI prediction (default = "recordings")
    
    confidence_allowance : float
        Confidence score allowance for emotions to be co-occurring (default = 0.05)
    ''' 
    video_processor = VideoProcessor(API_KEY, interval=5, recording_folder="recordings", confidence_allowance = 0.05)
    
    # Pattern Mining Algorithms
    seq_pattern_mine = PatternMine("PrefixSpan") # Prefix Span algorithm for Sequential Pattern Mining
    high_util_pattern_mine = PatternMine("Two-Phase") # Two-Phase algorithm for High Utility Pattern Mining
    freq_itemsets_pattern_mine = PatternMine("FPGrowth_itemsets") # FP-Growth algorithm for Frequent Itemsets Pattern Mining
    
    
    loop = asyncio.get_event_loop()
    video_processor.start_webcam()
    loop.run_until_complete(video_processor.process_video())

    time.sleep(5) # Delay to allow async tasks to clear
    print("Running Pattern Mining Algorithms...")
    # Sequential Pattern mining (Arguments: min_sup = 0.5, min_pat = 5)
    seq_pattern_mine.run("./results/extracted_sequence.txt", "./results/output_sequence.txt", 0.5, 5)
    # High Utility Pattern mining (Arguments: min_utility = 1)
    high_util_pattern_mine.run("./results/extracted_utility.txt", "./results/output_utility.txt", 1)
    # Frequent Itemsets Pattern mining (Arguments: min_sup = 40%)
    freq_itemsets_pattern_mine.run("./results/extracted_frequent_itemsets.txt", "./results/output_frequent_itemsets.txt", "40%")

if __name__ == "__main__":
    main()