# hume_api.py
import asyncio
from hume import HumeStreamClient
from hume.models.config import FaceConfig
import pandas as pd

class HumeAPI:
    def __init__(self, api_key, file_path):
        self.API_KEY = api_key
        self.FILE_PATH = file_path
        self.extracted_results = pd.DataFrame()

    def set_file_path(self, file_path):
        self.FILE_PATH = file_path

    def get_file_path(self):
        return self.FILE_PATH

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
        print(self.extracted_results)
        return self.extracted_results

    def sort_results(self, results):
        results.apply(lambda x: self.sort_emotions(x["emotions"]), axis=1)
        print(results)

    def sort_emotions(self, emotions):
        emotions.sort(key=lambda x: x['score'], reverse=True)

    def extract_emotions(self):
        self.extracted_results["emotion1"] = self.extracted_results.apply(lambda x: x["emotions"][0]["name"],axis=1)
        self.extracted_results["emotion1_score"] = self.extracted_results.apply(lambda x: x["emotions"][0]["score"],axis=1)
        self.extracted_results["emotion2"] = self.extracted_results.apply(lambda x: x["emotions"][1]["name"],axis=1)
        self.extracted_results["emotion2_score"] = self.extracted_results.apply(lambda x: x["emotions"][1]["score"],axis=1)
        self.extracted_results["emotion3"] = self.extracted_results.apply(lambda x: x["emotions"][2]["name"],axis=1)
        self.extracted_results["emotion3_score"] = self.extracted_results.apply(lambda x: x["emotions"][2]["score"],axis=1)
