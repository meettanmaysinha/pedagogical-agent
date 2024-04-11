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
        
        # # Dataframes to store individual config results
        self.extracted_results = pd.DataFrame()
        self.extracted_results_face = {}
        self.extracted_results_prosody = {}
        self.extracted_results_vburst = {}
        # Dataframe with compiled results
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
        # print(self.aggregated_results.loc[:, ["most_common_highest_scored_emotion","highest_scored_emotion","emotion_score"]])
        print(self.aggregated_results)
    
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

        # async with client.connect(config) as socket:
        #     result = await socket.send_file(self.FILE_PATH)
        #     with open(f'./{results_directory}/predictions.json', 'w', encoding='utf-8') as f:
        #         json.dump(result, f, ensure_ascii=False, indent=4)

        # Opening JSON file
        f = open(f'./{results_directory}/predictions.json')
        # returns JSON object as 
        # a dictionary
        result = json.load(f)

        # Extract Face predictions
        try:
            # Extract results from Hume API call
            face_results = result["face"]["predictions"]
            self.extracted_results_face = face_results
        except KeyError:
            print("No Faces Detected...")
            self.extracted_results_face = {}

        # Extract Prosody predictions
        try: 
            prosody_results = result["prosody"]["predictions"]
            self.extracted_results_prosody = prosody_results
        except KeyError:
            print("No Speech Prosody Detected...")
            self.extracted_results_prosody = {}
        
        # Extract Vocal Burst predictions
        try:
            vburst_results = result["vocal_burst"]["predictions"]
            self.extracted_results_vburst = vburst_results
        except KeyError:
            print("No Vocal Bursts Detected...")
            self.extracted_results_vburst = {}

        # Clean and aggregate results
        try:
            self.extract_emotions() # Store emotion predictions to CSV
            self.aggregate_emotions() # Get frequency of emotions
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
            print("Error Detecting Emotions, trying again...")
            self.aggregated_results = pd.DataFrame()

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

        except FileNotFoundError:
            # If the file doesn't exist, write the DataFrame with headers
            dataframe.to_csv(file_path, header=True, index=False)

    def sort_results(self, results):
        '''Sorts emotions by name in ascending order'''
        results.apply(lambda x: self.sort_emotions(x["emotions"]), axis=1)

    def sort_emotions(self, emotions):
        '''Sorts emotions by scores in descending order'''
        print(emotions)
        # No Predictions
        if len(emotions) == 0:
            return None
        emotions.sort(key=lambda x: x['score'], reverse=True)

    def extract_emotions(self):
        '''
        Collate emotions predictions from all model configs into a CSV
        '''
        try:
            extracted = {
                "face_predictions":str(self.extracted_results_face),
                "prosody_predictions":str(self.extracted_results_prosody),
                "vburst_predictions":str(self.extracted_results_vburst)
            }
            self.extracted_results = pd.DataFrame(extracted, index=[0])

        except KeyError as e:
            print("No predictions available: ", e)

    def average_predictions(self, emotions_list):
        '''Get average predictions of emotions for each group (face_id)'''
        try:
            df = pd.DataFrame()
            if (len(emotions_list)>0):
                # Iterate over the "emotions" column and concatenate the individual predictions
                for predictions_list in emotions_list:
                    temp_df = pd.DataFrame(predictions_list)
                    df = pd.concat([df, temp_df], ignore_index=True)

                # Group by "name" and calculate the mean score for each emotion
                grp_df = df.groupby("name", as_index=False)["score"].mean()

                # Sort the DataFrame by score in descending order
                grp_df.sort_values("score", ascending=False, inplace=True)

                # Convert the DataFrame to a dictionary with "name" as the key and the average score as the value
                avg_dict = grp_df.set_index("name")["score"].to_dict()
                return avg_dict

                # return grp_df
            else:
                return df
            
        except Exception as e:
            print(f"No values to aggregate: {e}")

    def aggregate_emotions(self):
        '''Get average emotion scores for each processed interval across all configs'''
        # Face Config
        try:
            # Average prediction scores of emotions for the interval (Face)
            averaged_emotions_face_dict = self.average_predictions(self.extracted_results_face["emotions"])
        except KeyError:
            print("No face predictions to aggregate") # No faces detected
            averaged_emotions_face_dict = {}
        
        # Prosody Config
        try:
            # Average prediction scores of emotions for the interval (Prosody)
            averaged_emotions_prosody_dict = self.average_predictions(self.extracted_results_prosody["emotions"])
        except KeyError:
            print("No prosody predictions to aggregate") # No speech detected
            averaged_emotions_prosody_dict = {}

        # Vocal Burst Config
        try:
            # Average prediction scores of emotions for the interval (Vocal Burst)
            averaged_emotions_vburst_dict = self.average_predictions(self.extracted_results_vburst["emotions"])
        except KeyError:
            print("No vocal burst predictions to aggregate") # No vocal bursts detected
            averaged_emotions_vburst_dict = {}

        try:
            # Late fusion of emotions
            averaged_emotions_combined_dict = self.average_dicts(averaged_emotions_face_dict,averaged_emotions_prosody_dict,averaged_emotions_vburst_dict)
            occurring_emotions_dict = self.get_occurring_emotions(averaged_emotions_combined_dict)

            self.aggregated_results["occurring_emotions_dict"] = [occurring_emotions_dict]
            self.aggregated_results["occurring_emotions"] = [list(occurring_emotions_dict.keys())]
            self.aggregated_results["occurring_emotions_scores"] = [list(occurring_emotions_dict.values())]
            print(self.aggregated_results)
            self.aggregated_results["occurring_emotions_encoded"] = self.aggregated_results.apply(lambda x: self.encode_emotions_list(x["occurring_emotions"]), axis=1)
        except Exception as e:
            print("Error aggregating emotions, ",e) # No faces detected

    def get_occurring_emotions(self, avg_emotions_dict, confidence_allowance=0.05):
        """
        Filter the occurring emotions from a dictionary of average emotion scores.

        Parameters:
            avg_emotions_dict (dict): A dictionary containing emotion names as keys
                and their corresponding average scores.
            confidence_allowance (float): A threshold representing the tolerance
                for deviations from the highest score. Emotions with scores lower
                than (highest_score - confidence_allowance) will be considered
                non-occurring. Default is 0.05.

        Returns:
            dict: A filtered dictionary containing only the occurring emotions
                whose scores are within the confidence allowance of the highest score.

        Example:
            >>> avg_emotions = {'joy': 0.8, 'sadness': 0.3, 'anger': 0.7}
            >>> filter = get_occurring_emotions(avg_emotions, confidence_allowance=0.1)
            >>> print(filter)
            {'joy': 0.8, 'anger': 0.7}

        """
        top_emotion_score = float(max(avg_emotions_dict.values()))
        def filter_occurring_emotions(emotion_score_pair):
            emotion, score = emotion_score_pair
            if score < top_emotion_score - confidence_allowance:
                return False # Filter out non-occurring emotions
            else:
                return True # Keep co-occurring emotions
        occurring_emotions = dict(filter(filter_occurring_emotions, avg_emotions_dict.items()))
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
            # When enough rows of emotions collected
            if len(collated_results) >= sequences:
                for i in range(len(collated_results)): # For each row
                    sequence_list = collated_results.loc[max(0, i - sequences + 1):i + 1,["occurring_emotions"]].values.tolist() # Update each row with last n sequences
                    collated_results.loc[i,["emotion_sequence"]] = sequence_list

                    # Map emotions in the sequence_list using map_emotions(k)
                    mapped_sequence = str([[self.map_emotions(emotion) for emotion in ast.literal_eval(sequence[0])] for sequence in sequence_list])

                    # Update emotion_sequence column with the mapped sequence
                    collated_results.loc[i, "emotion_sequence"] = mapped_sequence

                    # # For each row j
                    # for j in collated_results.loc[i,["emotion_sequence"]]:
                    #     print("Jvalue",j)
                    #     # For each sequence k in row j
                    #     for index, k in enumerate(ast.literal_eval(j)):
                    #         j[index] = self.map_emotions(k) # Map emotions to an emotion ID for PatternMine

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
                
                # Convert string representation to list
                collated_results["occurring_emotions"] = collated_results["occurring_emotions"].apply(lambda x: ast.literal_eval(x))
                collated_results["occurring_emotions_scores"] = collated_results["occurring_emotions_scores"].apply(lambda x: ast.literal_eval(x))
                collated_results["occurring_emotions_encoded"] = collated_results["occurring_emotions_encoded"].apply(lambda x: ast.literal_eval(x))

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

    def average_dicts(self, *dicts):
        '''
        Averages all emotions from the dictionaries. Excludes empty dictionaries from the average.
        '''
        # Filter out empty dictionaries
        non_empty_dicts = [d for d in dicts if d]

        # Check if there are any non-empty dictionaries
        if len(non_empty_dicts) == 0:
            return None  # No non-empty dictionaries found

        # Calculate the total sum of values across all non-empty dictionaries
        total_sum = {}
        for d in non_empty_dicts:
            for key, value in d.items():
                total_sum[key] = total_sum.get(key, 0) + value

        # Calculate the average
        average = {key: total_sum[key] / len(non_empty_dicts) for key in total_sum}

        return average