# video_processor.py

import os
import cv2
import time
import threading
import asyncio
import json
import subprocess
from packages.hume.Hume import HumeAPI
from packages.recording.Webcam import Webcam
from packages.recording.audio_recorder import AudioRecorder

class VideoProcessor:
    def __init__(self, api_key, file_path="../output_0", interval=5, recording_folder="recordings", confidence_allowance = 0.05):
        self.hume_api = HumeAPI(api_key, file_path, confidence_allowance) # Create instane of HumeAPI
        self.webcam = Webcam() # Create instance of Webcam
        self.audio = AudioRecorder() # Create instance of AudioRecorder
        self.interval = interval
        self.recording_folder = recording_folder

    def start_webcam(self):
        # self.webcam.start_AVrecording() # Start webcam
        self.webcam.start()
        self.audio.start()

    def combine_av(self, av_name,av_file_path = "./recordings/av_output/", audio_file_path = "./recordings/audio/", video_file_path = "./recordings/video/"):
        # print("Normal recording\nMuxing")
        # Create directory if it does not exist
        os.makedirs(av_file_path, exist_ok=True)
        
        # Map each AV output to a timestamp in a json file av_timestamps.json
        av_timestamps_file = "av_timestamps.json"
        with open(av_file_path+av_timestamps_file, "a+") as json_av:
            try:
                # JSON file is not empty
                json_av.seek(0)  # move file pointer to the beginning
                av_timestamps = json.load(json_av)
            except Exception as e:
                # JSON file is empty
                av_timestamps = {} # Creates empty dict
                print(e)
        
        unix_time = time.time() # Save timestamp of video to track
        av_timestamps[av_name] = str(unix_time)

        with open(av_file_path+av_timestamps_file, 'w') as json_av:
            json.dump(av_timestamps, json_av)
        
        # Combine audio and video recording (Limit to 5s - Anything longer will be cut off)
        cmd = f"ffmpeg -hide_banner -loglevel error -y -i {video_file_path + av_name}.mp4 -i {audio_file_path + av_name}.wav -c:v copy -c:a aac -t 5 {av_file_path + av_name}.mp4"
        subprocess.call(cmd, shell=True)

    async def process_video(self):
        start_time = time.time()
        # self.webcam.start_AVrecording() # Start webcam
        self.webcam.start()
        output_id = 0
        output_name = f"output_{output_id}"
        # out = self.webcam.save_AVrecording(video_name) # Save video clip
        self.audio.write_audio_file(output_name) # Save audio clip

        output_id += 1 # Begin recording for next clip
        output_name = f"output_{output_id}"

        out = self.webcam.write_video_file(output_name)
        buffer = 2 # Number of clips to buffer before running Hume API

        while self.webcam.is_opened:
            ret, frame = self.webcam.read()
            out.write(frame)
            cv2.imshow('Webcam Feed', frame)
            
            # If video length longer than 5s, save video (Hume Max Video Length is 5s)
            if time.time() - start_time > 5: 
                # out.release()
        
                # Set new AV ID and name for next clip
                print(f"Saving Recording: {output_name}")
                
                self.audio.write_audio_file(output_name) # Save current audio clip
                output_id += 1
                output_name = f"output_{output_id}"
                out = self.webcam.write_video_file(output_name) # Save current video clip (Creates next file with name "output_name")
                
                start_time = time.time()


                # Combine AV and start Hume after a number of recordings to allow buffer time for processing
                if output_id > buffer:
                    av_id = output_id - buffer
                    av_name = f"output_{av_id}"
                    av_file_path = f"./{self.recording_folder}/av_output/"

                    # Save AV clip
                    # print(f"New AV: {av_name}")
                    # self.webcam.save_AVrecording(av_name)
                    self.combine_av(av_name=av_name, av_file_path=av_file_path)

                    # Set AV clip path for Hume API
                    self.hume_api.set_file_path(f"{av_file_path + av_name}.mp4")
                    # print(self.hume_api.get_file_path())

                    # Run Hume API in a separate thread
                    thread = threading.Thread(target=self.hume_api.handle_hume_call, args=[av_id])
                    thread.start()

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # self.webcam.stop_AVrecording()
        self.webcam.release()
        cv2.destroyAllWindows()
        self.audio.stop()
