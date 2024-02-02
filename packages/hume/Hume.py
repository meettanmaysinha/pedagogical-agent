# hume_api.py
import asyncio
from hume import HumeStreamClient
from hume.models.config import FaceConfig, ProsodyConfig
# from packages.emotionpattern.PatternMine import PatternMine
from packages.emotionpattern.emotions_dict import emotions_dict
import pandas as pd
import os
import json
import ast

class HumeAPI:
    def __init__(self, api_key, file_path, confidence_allowance=0.05):
        """Creates instance of HumeAI API to get emotions predictions
        Parameters
        ----------
        api_key: str
            API Key for HumeAI
        
        file_path: str
            File path of recording for HumeAI prediction
        
        confidence_allowance : float
            Confidence score allowance for emotions to be co-occurring (default = 0.05)
        """
        self.API_KEY = api_key
        self.FILE_PATH = file_path
        self.confidence_allowance = confidence_allowance
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
        print(self.aggregated_results.loc[:, ["most_common_highest_scored_emotion","highest_scored_emotion","emotion_score"]])
    
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
        # Create directory if it does not exist
        results_directory = './results'
        os.makedirs(results_directory, exist_ok=True)
        
        client = HumeStreamClient(self.API_KEY) # Create Hume client
        config = [FaceConfig(identify_faces=True), ProsodyConfig()] # Create Hume config

        async with client.connect(config) as socket:
            result = await socket.send_file(self.FILE_PATH)
            with open(f'./{results_directory}/predictions.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

        # Opening JSON file
        f = open(f'./{results_directory}/predictions.json')
        # returns JSON object as 
        # a dictionary
        result = json.load(f)

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
            
            self.results_to_csv(self.extracted_results, "./results/extracted_emotions.csv", mode="a") # Append results to extracted_emotions.csv
            self.results_to_csv(self.aggregated_results, "./results/aggregated_emotions.csv", mode="a") # Append results to aggregated_emotions.csv

            self.extract_sequence(sequences=4) # Get last 4 predicted emotions for each prediction of emotions
            self.extract_utility() # Get utility for emotions 
            self.extract_frequent_itemsets() # Get frequent itemsets for frequent itemset mining

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

    def average_predictions(self, group_df):
        '''Get average predictions of emotions for each group (face_id)'''
        try:
            df = pd.DataFrame()

            # Iterate over the "emotions" column and concatenate the individual predictions
            for predictions_list in group_df["emotions"]:
                temp_df = pd.DataFrame(predictions_list)
                df = pd.concat([df, temp_df], ignore_index=True)

            # Group by "name" and calculate the mean score for each emotion
            grp_df = df.groupby("name")["score"].mean().reset_index()

            # Sort the DataFrame by score in descending order
            grp_df.sort_values("score", ascending=False, inplace=True)

            # Convert the DataFrame to a dictionary with "name" as the key and the average score as the value
            avg_dict = grp_df.set_index("name")["score"].to_dict()

            return avg_dict
        
        except Exception as e:
            print(f"An error occurred: {e}")

    def aggregate_emotions(self):
        '''Get highest scored and most frequent emotions for each processed interval'''
        try:
            # Highest scored emotion in the interval
            highest_scored_emotion = (
                self.extracted_results.loc[self.extracted_results
                .groupby(["face_id"])["emotion1_score"]
                .idxmax(), ["face_id", "emotion1", "emotion1_score"]]
            )

            # Most common emotion in the interval
            most_common_emotion = (
                self.extracted_results.groupby(["face_id", "emotion1"])
                .size().reset_index(name="count")
                .sort_values("count", ascending=False)
                .groupby("face_id")
                .first()
                .reset_index()
            )

            # Average prediction scores of emotions for the interval
            averaged_emotions = self.extracted_results.groupby("face_id").apply(self.average_predictions).reset_index()
            averaged_emotions.rename(columns={averaged_emotions.columns[1]:"averaged_emotions"}, inplace=True) # Rename
            
            # Extract dominant emotions by score including co-occurring emotions
            averaged_emotions["dominant_emotions"] = averaged_emotions.apply(lambda x: self.get_occurring_emotions(x["averaged_emotions"]), axis=1)

            # Renaming columns
            highest_scored_emotion.rename(columns={"emotion1": "highest_scored_emotion", "emotion1_score": "emotion_score"}, inplace=True)
            most_common_emotion.rename(columns={"emotion1": "most_common_highest_scored_emotion", "count": "emotion_count"}, inplace=True)
            
            # Join the results together
            self.aggregated_results = highest_scored_emotion.merge(most_common_emotion, on="face_id", how="left")
            self.aggregated_results = self.aggregated_results.merge(averaged_emotions, on="face_id", how="left")

            # For each row in the dataframe, get occurring emotions and confidence score
            # self.aggregated_results["dominant_emotions"] = self.aggregated_results["dominant_emotions"].apply(lambda x: ast.literal_eval(x)) # Convert string to dictionary
            self.aggregated_results["occurring_emotions"] = self.aggregated_results["dominant_emotions"].apply(lambda x: list(x.keys()))
            self.aggregated_results["occurring_emotions_scores"] = self.aggregated_results["dominant_emotions"].apply(lambda x: list(x.values()))
            self.aggregated_results["occurring_emotions_encoded"] = self.aggregated_results["occurring_emotions"].apply(lambda x: self.encode_emotions_list(x))

        except Exception as e:
            print("Error aggregating emotions, ",e)
            pass # No faces detected

    def get_occurring_emotions(self, avg_emotions_dict, confidence_allowance=0.05):
        top_emotion_score = float(max(avg_emotions_dict.values()))
        def filter_occurring_emotions(emotion_score_pair):            
            emotion, score = emotion_score_pair
            if score < top_emotion_score - confidence_allowance:
                return False # Filter out non-occurring emotions
            else:
                return True # Keep co-occurring emotions
        occurring_emotions = dict(filter(filter_occurring_emotions, avg_emotions_dict.items()))
        print(filter(filter_occurring_emotions, avg_emotions_dict.items()))
        return occurring_emotions

    def encode_emotions_list(self, emotions_list):
        '''
        Encodes emotions to emotion ID
        '''
        encoded_emotions = []
        for emotion in emotions_list:
            encoded_emotions.append(self.map_emotions(emotion))
        return encoded_emotions
     
    # For Sequential Pattern Mining (ie. PrefixSpan)
    # Currently inefficient, rewrites the entire column per iteration
    # "sequences" argument determines how many past sequences(rows) of emotions to consider
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
                    print("Not enough rows to get sequence") # Let Hume run a few more times to gather enough data for seq pattern mining
        except Exception as e:
            print(e," Error extracting sequence")
            pass
   
    # For High Utility Pattern Mining (ie. TwoPhase)
    def extract_utility(self):
        '''
        Extracts confidence from emotions predictions as utility
        '''
        
        try:    
                # Load aggregated emotions
                collated_results = pd.read_csv("./results/aggregated_emotions.csv")
                
                collated_results["occurring_emotions"] = collated_results["occurring_emotions"].apply(lambda x: ast.literal_eval(x)) # Convert from string representation 
                collated_results["occurring_emotions_scores"] = collated_results["occurring_emotions_scores"].apply(lambda x: ast.literal_eval(x)) # Convert from string representation 
                collated_results["occurring_emotions_encoded"] = collated_results["occurring_emotions_encoded"].apply(lambda x: ast.literal_eval(x)) # Convert from string representation 

                # For each row in the dataframe, get occurring emotions and confidence score
                collated_results["occurring_emotions_scores_total"] = collated_results["occurring_emotions_scores"].apply(lambda x: sum(x))

                # Multiply scale by 100 and round to integer for High Utility Pattern Mining input
                collated_results["occurring_emotions_scores"] = collated_results["occurring_emotions_scores"].apply(lambda x: [round(i * 100) for i in x]) # Error here
                collated_results["occurring_emotions_scores_total"] = collated_results["occurring_emotions_scores_total"]*100
                collated_results["occurring_emotions_scores_total"] = collated_results["occurring_emotions_scores_total"].astype(int)
        
                # Export utility to file
                self.export_utility(collated_results,"./results/extracted_utility.txt")

        except Exception as e:
            print(e," Error extracting utility")
            pass
    
    # For Frequent Item Set Mining
    def extract_frequent_itemsets(self):
        '''
        Extracts predicted emotions into sets for Frequent Item Set Mining
        '''
        try:
            # Load aggregated emotions
            collated_results = pd.read_csv("./results/aggregated_emotions.csv")

            # Encode emotions to emotion ID
            collated_results["occurring_emotions_encoded"] = collated_results["occurring_emotions_encoded"].apply(lambda x: ast.literal_eval(x)) # Convert from string representation 

            # Export utility to file
            self.export_frequent_itemsets(collated_results,"./results/extracted_frequent_itemsets.txt")

        except Exception as e:
            print(e," Error extracting Frequent Item Sets")
            pass
    
    def map_emotions(self, emotion):
        return emotions_dict[emotion]
    
    def export_sequence(self, results, filepath):
        '''
        Exports sequences into fixed format for Sequence Mining
        '''
        results["emotion_sequence"] = (
            results["emotion_sequence"].apply(lambda x: str(x)
                                              .replace("[","")
                                              .replace("]"," -1 -2") # End indicator
                                              .replace(","," -1") # Separator
                                              .replace("'",""))
        )
        
        results["emotion_sequence"].to_csv(filepath, index=False, header=False)
        
    def export_utility(self, results, filepath):
        '''
        Exports dominant emotions into fixed format for High Utility 
        '''
        # Join scores into a single string
        results["occurring_emotions_scores"] = results["occurring_emotions_scores"].apply(lambda x: " ".join(map(str,x)))
        # Join Emotions, Total Confidence Scores and Individual Confidence Scores into a single string for Pattern mining
        results["utility_encoded"] = results.apply(lambda x:"".join([
            # Encoded Emotions
            str(x["occurring_emotions_encoded"]).replace("[","").replace("]","").replace(",","").replace("'",""),
            ":", # Separator
            # Total confidence scores
            str(x["occurring_emotions_scores_total"]),
            ":", # Separator
            # Individual scores 
            str(x["occurring_emotions_scores"]).replace("[","").replace("]","").replace(",","").replace("'",""),
        ]), axis = 1)

        results["utility_encoded"].to_csv(filepath, index=False, header=False)

    def export_frequent_itemsets(self, results, filepath):
        '''
        Exports dominant emotions into fixed format for Frequent Itemset Mining
        '''
        # Join Encoded Itemsets into string and remove brackets
        results["itemsets_encoded"] = results.apply(lambda x:"".join([
            # Encoded Emotions
            str(x["occurring_emotions_encoded"]).replace("[","").replace("]","").replace(",","").replace("'","")
        ]), axis = 1)

            
        results["itemsets_encoded"].to_csv(filepath, index=False, header=False)

