import cv2
import sounddevice as sd
import time
import asyncio
import nest_asyncio
nest_asyncio.apply()
from concurrent.futures import ThreadPoolExecutor
from VideoCaptureThreading import VideoCaptureThreading
import apikey

import pandas as pd
import numpy as np

from hume import HumeStreamClient, StreamSocket
from hume.models.config import FaceConfig

API_KEY = apikey.API_KEY
FILE_PATH = "videos/frustrated_trim.mp4"
def sort_emotions(emotions):
    # Sort emotions by scores
    emotions.sort(key=lambda x: x['score'],reverse=True)
    emotions

def sort_results(results):
    results.apply(lambda x: sort_emotions(x["emotions"]),axis=1)
    print(results)
def run_in_executor_blocking(func, *args):
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(ThreadPoolExecutor(), func, *args)
    
async def humeCall():
    print("Hume Call Start")
    client = HumeStreamClient(API_KEY)
    config = FaceConfig(identify_faces=True)
    
    async with client.connect([config]) as socket:
        result =  await socket.send_file(FILE_PATH)
    
    print(f"File Path = {FILE_PATH}")
    

    # print(result)
    try:
        results = result["face"]["predictions"]
    except:
        print("No Faces Detected")
        results = {}

    # print(results)

    global extracted_results
    extracted_results = pd.json_normalize(results)
        
    sort_results(extracted_results)
    print(extracted_results)
    return extracted_results

def startWebcam():
    # Open the webcam (you may need to change the argument to the appropriate camera index)
    cap = cv2.VideoCapture(0)
    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

    videoWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    videoHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return cap, fourcc, videoWidth, videoHeight
async def start_video(video_id,fourcc, videoWidth, videoHeight):
    return cv2.VideoWriter(f'./.mp4/output_{video_id}.mp4', fourcc, 60.0, (videoWidth, videoHeight))
async def process_video(cap, fourcc, videoWidth, videoHeight):
    start_time = time.time()
    video_id = 0
    out = cv2.VideoWriter(f'./.mp4/output_{video_id}.mp4', fourcc, 60.0, (videoWidth, videoHeight))

    while cap.isOpened():
        ret, frame = cap.read()
        out.write(frame)
        cv2.imshow('Webcam Feed', frame)

        if time.time() - start_time > 5:
            out.release()
            print(f"Run: {video_id}")

            global FILE_PATH
            FILE_PATH = f"./.mp4/output_{video_id}.mp4"
            print(FILE_PATH)
            
            video_id += 1
            start_time = time.time()

            humeTask = await asyncio.gather(start_video(video_id, fourcc, videoWidth, videoHeight),humeCall())

        
            out = humeTask[0]

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


cap, fourcc, videoWidth, videoHeight= startWebcam()
# Run the event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(process_video(cap, fourcc, videoWidth, videoHeight))
