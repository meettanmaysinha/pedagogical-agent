import os
import subprocess
import pandas as pd
from hume import HumeBatchClient
from hume.models.config import FaceConfig
from hume.models.config import ProsodyConfig
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("HUME_API_KEY")

class FileProcessor:
    def __init__(self, configs=[FaceConfig(),ProsodyConfig()], file_path=None):
        '''Initialise Hume Batch API'''
        self.client = HumeBatchClient(API_KEY)
        self.configs = configs
        self.file_path = file_path if isinstance(file_path, list) else [file_path]

    def set_filepath(self,file_path):
        '''Sets file path of clip being analysed'''
        self.file_path = file_path

    def process_file(self):
        '''Processes file using Hume API'''
        job = self.client.submit_job(None, self.configs, files=self.file_path)
        
        print(job)
        print("Running...")

        job.await_complete()
        predictions = job.get_predictions()
        job.download_predictions("predictions.json")
        print("Predictions downloaded to predictions.json")
        return predictions

    # Not implemented yet
    def split_file(self, interval = 10):
        '''Splits large file into chunks for Hume API call'''
        file_size_limit = 100000000 # 100MB
        cmd = f"python ffmpeg-split.py -f big_video_file.mp4 -s {interval} -S {file_size_limit}"
        subprocess.call(cmd, shell=True)

class EmotionsAnalyser:
        # self.dataframe = None

    def display_file_details(self, prediction=None):
        '''Displays file details, such as type and filename'''
        print(prediction[0]["source"])
    
    def to_dataframe(self, prediction=None):
        '''Converts face and prosody results to a dataframe'''
        face_dataframe, prosody_dataframe = pd.DataFrame(), pd.DataFrame()
        if "face" in prediction[0]["results"]["predictions"][0]["models"]:
            # Extract results from Face model
            face_dataframe = pd.json_normalize(prediction[0]["results"]["predictions"][0]["models"]["face"]["grouped_predictions"][0]["predictions"])
            face_dataframe.apply(lambda x: self.sort_emotions(dataframe=x["emotions"]),axis=1)
            self.extract_top_3_emotions(dataframe=face_dataframe)

        if "prosody" in prediction[0]["results"]["predictions"][0]["models"]:
            # Extract results from Prosody model
            prosody_dataframe = pd.json_normalize(prediction[0]["results"]["predictions"][0]["models"]["prosody"]["grouped_predictions"][0]["predictions"])
            prosody_dataframe.apply(lambda x: self.sort_emotions(dataframe=x["emotions"]),axis=1)
            self.extract_top_3_emotions(dataframe=prosody_dataframe)
        
        return face_dataframe, prosody_dataframe
    
    def sort_emotions(self, dataframe=None,sort_by='score',reverse=True):
        # Sort emotions by scores
        dataframe.sort(key=lambda x: x[sort_by],reverse=reverse)
        # return dataframe

    def extract_top_3_emotions(self, dataframe=None):
        # Get list of top 3 emotions
        dataframe["top3_emotions"] = dataframe.apply(lambda x: x["emotions"][:3],axis=1)
        # Individually extract top 3 emotions
        dataframe["first_emotion"] = dataframe.apply(lambda x: x["emotions"][0]["name"],axis=1)
        dataframe["first_emotion_score"] = dataframe.apply(lambda x: x["emotions"][0]["score"],axis=1)
        dataframe["second_emotion"] = dataframe.apply(lambda x: x["emotions"][1]["name"],axis=1)
        dataframe["second_emotion_score"] = dataframe.apply(lambda x: x["emotions"][1]["score"],axis=1)
        dataframe["third_emotion"] = dataframe.apply(lambda x: x["emotions"][2]["name"],axis=1)
        dataframe["third_emotion_score"] = dataframe.apply(lambda x: x["emotions"][2]["score"],axis=1)
        # return dataframe

    def most_common_occurence(self, dataframe=None):
        # Get most common emotion
        try:
            most_common_emotion = dataframe['first_emotion'].value_counts().idxmax()
            most_common_emotion_occurences = dataframe['first_emotion'].value_counts()[most_common_emotion]
            return most_common_emotion, most_common_emotion_occurences
        except:
            return None, None
        
    def export_results(self, dataframe=None, filename="results.csv"):
        # Export dataframe to csv
        dataframe.to_csv(filename,index=False)

# # Example usage
# # FILE_PATH = ["/Users/chengyao/Downloads/Hume_Test_Video_Football.mp3"]
# FILE_PATH = ["/Users/chengyao/Downloads/Test_Hume_Comedian.mp4"]
# configs = [FaceConfig(), ProsodyConfig()]
# processor = FileProcessor(configs,file_path=FILE_PATH)

# predictions = processor.process_file()
# analyser = EmotionsAnalyser()
# analyser.display_file_details(predictions)
# face_df, prosody_df = analyser.to_dataframe(predictions)
# analyser.export_results(face_df,"face_results.csv")
# analyser.export_results(prosody_df,"prosody_results.csv")
# print("The most common facial occurence of emotion is: ", (analyser.most_common_occurence(dataframe=face_df)))
# print("The most common prosody occurence of emotion is: ", (analyser.most_common_occurence(dataframe=prosody_df)))