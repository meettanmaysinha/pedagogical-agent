# hume_api.py
import asyncio
from hume import HumeStreamClient
from hume.models.config import FaceConfig, ProsodyConfig
# from packages.emotionpattern.PatternMine import PatternMine
from packages.emotionpattern.emotions_dict import emotions_dict
import pandas as pd
import os

class HumeAPI:
    def __init__(self, api_key, file_path):
        self.API_KEY = api_key
        self.FILE_PATH = file_path
        self.extracted_results = pd.DataFrame()
        self.aggregated_results = pd.DataFrame()
        # self.pattern_mine = PatternMine()

    def set_file_path(self, file_path):
        '''Sets file path of clip being analysed'''
        self.FILE_PATH = file_path

    def get_file_path(self):
        '''Returns file path of clip being analysed'''
        return self.FILE_PATH
    
    def print_results(self):
        '''Prints results of each Hume call'''
        print(self.aggregated_results.loc[:, ["most_common_emotion","highest_scored_emotion","emotion_score"]])
    
    def write_results(self):
        '''Appends results of each Hume call to results CSV file'''
        self.extracted_results.to_csv("./results/results.csv", mode='a')  

    def handle_hume_call(self, video_id=-1):
        '''Handles Hume API call'''
        loop = asyncio.new_event_loop() # Create new event loop
        asyncio.set_event_loop(loop) # Set event loop
        loop.run_until_complete(self.hume_call(video_id)) # Run Hume API call
        loop.close()

    async def hume_call(self,video_name="test"):
        '''Performs Hume API call asynchronously'''
        print("Hume Call Start")
        client = HumeStreamClient(self.API_KEY) # Create Hume client
        config = [FaceConfig(identify_faces=True), ProsodyConfig()] # Create Hume config

        async with client.connect(config) as socket:
            result = await socket.send_file(self.FILE_PATH)

        print(f"File Path = {self.FILE_PATH}")

        try:
            # Extract results from Hume API call
            results = result["face"]["predictions"]
            self.extracted_results = pd.json_normalize(results)

            self.sort_results(self.extracted_results)
            self.extract_emotions() # Get top 3 emotions

            self.aggregate_emotions() # Get frequency of emotions

            self.print_results()
            
            # Attach video id to results to determine sequence of videos
            self.extracted_results["video_name"] = video_name
            self.aggregated_results["video_name"] = video_name
            
            # Create directory if it does not exist
            results_directory = './results'
            os.makedirs(results_directory, exist_ok=True)
            
            self.results_to_csv(self.extracted_results, "./results/extracted_emotions.csv", mode="a") # Append results to extracted_emotions.csv
            self.results_to_csv(self.aggregated_results, "./results/aggregated_emotions.csv", mode="a") # Append results to aggregated_emotions.csv

            self.extract_sequence(sequences=4) # Get last 4 predicted emotions for each prediction of emotions

            return self.aggregated_results
            
        except Exception as e:
            print(e)
            print("Error Detecting Faces, trying again...")
            self.aggregated_results = {}

        return self.aggregated_results

    def results_to_csv(self, dataframe, file_path, mode='a'):
        '''Writes results to CSV file'''
        # Check if the file already exists
        try:
            # Read the first row of the existing file
            with open(file_path, 'r') as file:
                file.readline().strip()

            # Determine whether to write headers based on the existing file
            headers_exist = pd.notna(pd.read_csv(file_path, nrows=0).columns).any()

            # Write the DataFrame to the file without headers if they already exist
            dataframe.to_csv(file_path, mode=mode, header=not headers_exist, index=False)

        except:
            # If the file doesn't exist, write the DataFrame with headers
            dataframe.to_csv(file_path, header=True, index=False)


    def sort_results(self, results):
        '''Sorts emotions by name in ascending order'''
        results.apply(lambda x: self.sort_emotions(x["emotions"]), axis=1)

    def sort_emotions(self, emotions):
        '''Sorts emotions by scores in descending order'''
        emotions.sort(key=lambda x: x['score'], reverse=True)

    def extract_emotions(self):
            '''Get top emotions'''
        # try:
            # Extract top 3 emotions
            self.extracted_results["top3_emotions"] = self.extracted_results.apply(lambda x: x["emotions"][:3],axis=1)
            # Extract most dominant emotion
            self.extracted_results["emotion1"] = self.extracted_results.apply(lambda x: x["emotions"][0]["name"],axis=1)
            self.extracted_results["emotion1_score"] = self.extracted_results.apply(lambda x: x["emotions"][0]["score"],axis=1)
            # Extract second most dominant emotion
            self.extracted_results["emotion2"] = self.extracted_results.apply(lambda x: x["emotions"][1]["name"],axis=1)
            self.extracted_results["emotion2_score"] = self.extracted_results.apply(lambda x: x["emotions"][1]["score"],axis=1)
            # Extract third most dominant emotion
            self.extracted_results["emotion3"] = self.extracted_results.apply(lambda x: x["emotions"][2]["name"],axis=1)
            self.extracted_results["emotion3_score"] = self.extracted_results.apply(lambda x: x["emotions"][2]["score"],axis=1)
        # except:
        #     print("No faces detected")
        #     pass

    def aggregate_emotions(self):
        '''Get highest scored and most frequent emotions'''
        try:
            # Highest scored emotion
            highest_scored_emotion = (
                self.extracted_results.loc[self.extracted_results
                .groupby(["face_id"])["emotion1_score"]
                .idxmax(), ["face_id", "emotion1", "emotion1_score"]]
            )

            # Most common emotion
            most_common_emotion = (
                self.extracted_results.groupby(["face_id", "emotion1"])
                .size().reset_index(name="count")
                .sort_values("count", ascending=False)
                .groupby("face_id")
                .first()
                .reset_index()
            )

            highest_scored_emotion = highest_scored_emotion.rename(columns={"emotion1": "highest_scored_emotion", "emotion1_score": "emotion_score"})
            most_common_emotion = most_common_emotion.rename(columns={"emotion1": "most_common_emotion", "count": "emotion_count"})

            # Join the two results together
            self.aggregated_results = highest_scored_emotion.merge(most_common_emotion, on="face_id", how="left")

        
        except:
            pass # No faces detected

    # Currently inefficient, rewrites the entire column per iteration
    # sequences determine how many past sequences of emotions to consider
    def extract_sequence(self, sequences):
        try:
                collated_results = pd.read_csv("./results/aggregated_emotions.csv")
                # Initialise column sequence
                collated_results["emotion_sequence"] = ""
                if len(collated_results) >= sequences:
                    for i in range(len(collated_results)):
                        collated_results.loc[i,["emotion_sequence"]] = collated_results.loc[max(0, i - sequences + 1):i + 1,["highest_scored_emotion"]].values.tolist() 
                        for j in collated_results.loc[i,["emotion_sequence"]]:
                            for index, k in enumerate(j):
                                j[index] = self.map_emotions(k) # Map emotions to an emotion ID for PatternMine


                    self.export_sequence(collated_results,"./results/extracted_sequence.txt")
                else:
                    print("Not enough rows to get sequence")
        except Exception as e:
            print(e," Error extracting sequence")
            pass

    def map_emotions(self, emotion):
        return emotions_dict[emotion]
    
    def export_sequence(self, results, filepath):
        results["emotion_sequence"] = (
            results["emotion_sequence"].apply(lambda x: str(x)
                                              .replace("[","")
                                              .replace("]"," -1 -2") # End indicator
                                              .replace(","," -1") # Separator
                                              .replace("'",""))
        )
        
        results["emotion_sequence"].to_csv(filepath, index=False, header=False)
        
