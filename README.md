<!-- GETTING STARTED -->
## Getting Started
### Prerequisite
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)   						![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white)

### Installation

1. Install Python packages
   ```sh
   pip install requirements.txt
   ```
2. Create a file called `api_key.py` *(Already Created)*
   ```py
   const API_KEY = 'ENTER YOUR API';
   ```

<!-- FILES -->
## Files

#### Main Classes
    .
    ├── main.py					# Main file to run
    ├── VideoProcessor.py		# Activates webcam and handles Hume API calls
    ├── VideoAudioRecorder.py	# Currently unused - For audio recording
    ├── Webcam.py				# Handles webcam input 
    ├── Hume.py					# Hume API calls
    ├── PatternMine.py			# Sequential Pattern Mining
    └── spmf.jar				# Algorithms for Pattern Mining
    

#### Text/CSV Files
    .
    ├── extracted_emotions.csv			# Predictions of Hume AI
    ├── aggregated_emotions.csv			# Aggregated and cleaned results
    ├── extracted_sequence.txt			# Input sequence of emotions for Sequence Mining
    ├── output_sequence.txt				# Output results of Sequence Mining
    └── emotions_dict.py				# Dictionary mapping emotions with Emotion ID (for sequence mining)


<!-- USAGE -->
## Usage

1. Configure processing interval in `main.py`, changing the interval parameter
   ```py
   video_processor  =  VideoProcessor(API_KEY, interval=5)
   ```
   
	
2. Run the `main.py` file in terminal:
   ```py
   python main.py
   ```

3. Allow access to Camera and the video feed should start
4. While the video feed is running, emotions predictions will be printed in the terminal and also saved into `extracted_emotions.csv` and `aggregated_emotions.csv`
5. Video feed will be saved at every fixed interval *(default 5 sec)* into the `/.mp4` folder
6. Sequences will be extracted into `extracted_sequence.txt` and encoded using Emotion IDs in `emotions_dict.py` 
7. To close the video feed, press 'Q' on your keyboard
8. Sequence mining algorithm will then run and output will be printed in `output_sequence.txt`



<!-- OUTPUT -->
## Output

### Videos
Video clips will be saved in the `/.mp4`  folder according to the interval set in `main.py`

Each clip is sent through an API call to Hume, returning predictions for emotion

### Prediction Results
#### Extracted Predictions
Prediction results from Hume is extracted into the `extracted_emotions.csv` file, which shows the prediction results, along with the top 3 emotions and their prediction scores. The sequence of video ID is also attached.
  ```json
{
	  "frame": 20,
	  "time": null,
	  "prob": 0.9996715784072876,
	  "face_id": "face_0",
	  "emotions": "[{'name': 'Disappointment', 'score': 0.36673504114151}, {'name': 'Sadness', 'score': 0.3661433458328247},  
	  "bbox": {
	    "x": 1168.461181640625,
	    "y": 570.3857421875,
	    "w": 272.525390625,
	    "h": 412.23681640625
	  },
	  "top3_emotions": "[{'name': 'Disappointment', 'score': 0.36673504114151}, {'name': 'Sadness', 'score': 0.3661433458328247}, {'name': 'Tiredness', 'score': 0.36571288108825684}]",
	  "emotion1": "Disappointment",
	  "emotion1_score": 0.36673504114151,
	  "emotion2": "Sadness",
	  "emotion2_score": 0.3661433458328247,
	  "emotion3": "Tiredness",
	  "emotion3_score": 0.36571288108825684,
	  "video_id": 1
}
   ```

#### Summarised Predictions   
Results are then aggregated into `aggregated_emotions.csv` which identifies the emotion with highest prediction score, and the most frequently shown emotion in each interval.
  ```json
   {
	  "face_id": "face_0",
	  "highest_scored_emotion": "Sadness",
	  "emotion_score": 0.5206286311149597,
	  "most_common_emotion": "Disappointment",
	  "emotion_count": 1,
	  "video_id": 1
	}
   ```
   
#### Sequences of Emotions
After the video feed is ended by pressing 'Q' on the keyboard, the Sequence Mining Algorithm will run and generate an output `output_sequence.txt` that show the most frequently occuring sequence

  ```
  Example Output:
  
Boredom | #SUP: 50
Boredom | Boredom | #SUP: 47
Boredom | Boredom | Boredom | #SUP: 39
Boredom | Boredom | Boredom | Boredom | #SUP: 27
   ```

`|` represents the divider between item sets
`#SUP` indicates the support of the pattern in the dataset



# Resources

[SPMF PrefixSpan Documentation](https://www.philippe-fournier-viger.com/spmf/PrefixSpan.php)


