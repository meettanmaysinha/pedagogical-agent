# hume_api.py
import asyncio
from hume import HumeStreamClient
from hume.models.config import FaceConfig
# from PatternMine import PatternMine
import pandas as pd

class HumeAPI:
    def __init__(self, api_key, file_path):
        self.API_KEY = api_key
        self.FILE_PATH = file_path
        self.extracted_results = pd.DataFrame()
        self.aggregated_results = pd.DataFrame()
        # self.pattern_mine = PatternMine()

    def set_file_path(self, file_path):
        self.FILE_PATH = file_path

    def get_file_path(self):
        return self.FILE_PATH
    
    def print_results(self):
        print(self.extracted_results["top3_emotions"])
    
    def write_results(self):
        self.extracted_results.to_csv("results.csv", mode='a')  

    def handle_hume_call(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.hume_call())
        loop.close()

    async def hume_call(self):
        print("Hume Call Start")
        client = HumeStreamClient(self.API_KEY)
        config = FaceConfig(identify_faces=True)

        async with client.connect([config]) as socket:
            result = await socket.send_file(self.FILE_PATH)

        print(f"File Path = {self.FILE_PATH}")

        try:
            results = result["face"]["predictions"]
        except:
            print("No Faces Detected")
            results = {}

        self.extracted_results = pd.json_normalize(results)

        self.sort_results(self.extracted_results)
        self.extract_emotions()

        self.print_results()

        self.aggregate_emotions()
        # print(self.aggregated_results)

        self.results_to_csv(self.extracted_results, "extracted_emotions.csv")
        self.results_to_csv(self.aggregated_results, "aggregated_emotions.csv")
        
        return self.extracted_results

    def results_to_csv(self, dataframe, file_path):
        # Check if the file already exists
        try:
            # Read the first row of the existing file
            with open(file_path, 'r') as file:
                first_line = file.readline().strip()

            # Determine whether to write headers based on the existing file
            headers_exist = pd.notna(pd.read_csv(file_path, nrows=0).columns).any()

            # Write the DataFrame to the file without headers if they already exist
            dataframe.to_csv(file_path, mode='a', header=not headers_exist, index=False)

        except:
            # If the file doesn't exist, write the DataFrame with headers
            dataframe.to_csv(file_path, header=True, index=False)


    def sort_results(self, results):
        results.apply(lambda x: self.sort_emotions(x["emotions"]), axis=1)

    def sort_emotions(self, emotions):
        emotions.sort(key=lambda x: x['score'], reverse=True)

    def extract_emotions(self):
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

    def aggregate_emotions(self):
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
        # Sequence of emotions
        emotion_sequence = (
            self.extracted_results.groupby("face_id")["emotion1"]
            .apply(list)
            .reset_index(name='sequence')
        )

        highest_scored_emotion = highest_scored_emotion.rename(columns={"emotion1": "highest_scored_emotion", "emotion1_score": "emotion_score"})
        most_common_emotion = most_common_emotion.rename(columns={"emotion1": "most_common_emotion", "count": "emotion_count"})
    
        aggregated_results = highest_scored_emotion.merge(most_common_emotion, on="face_id", how="left")
        self.aggregated_results = aggregated_results.merge(emotion_sequence, on="face_id", how="left")
        print(self.aggregated_results)


