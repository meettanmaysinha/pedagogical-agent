<!-- GETTING STARTED -->
## Getting Started

### Introduction

This Pedagogical Agent is designed to provide adaptive scaffolding through the introduction of emotional analysis and response generation using Large Language Models (LLMs). This documentation is your comprehensive guide to making the most of our application.

For development, refer to the Development section at the end of this README

### **Key Features**

Here are some of the key features of the Pedagogical Agent:

- **Feature 1**: Emotions Analysis
- **Feature 2**: Response Generation with LLMs
- **And More (In development)**: Pattern Mining of Results

### Prerequisites
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)   						![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white)

### Installation

1. Install Python packages
   ```sh
   $ pip install -r requirements.txt
   ```

2. Install FFmpeg on your device

   #### MacOS (Homebrew required):
   ```sh
   brew install ffmpeg
   ```

   #### For Windows, follow [these](https://phoenixnap.com/kb/ffmpeg-windows) instructions

3. Create a file called `.env`
   
   ```py
   HUME_API_KEY = 'HUME_API_KEY'
   OPENAI_API_KEY = 'OPENAI_API_KEY'
   ```
   *API Keys to be reset before deployment, .env to be added to .gitignore*

<!-- Scripts -->
## Main Scripts

### Webcam Stream

   ```sh
   python streammain.py
   ```
   Webcam will turn on and recordings will be saved in the `./recordings` folder
   * Video recording will be saved in `./recordings/video` 
   * Audio recording will be saved in `./recordings/audio`
   * Combined recording will be saved in `./recordings/av_output`

#### Closing the Webcam program

1. To close the Webcam Stream, press 'Q' on the keyboard

2. Then run the following command in the command line
   ```sh
   npx kill-port 8000
   ```

### Batch Upload
   ```sh
   streamlit run batchmain.py
   ```

   Open the Streamlit link on browser to access the interface
   * Upload an audio/video file (WAV, MP3, M4A, MP4, AVI, MPEG4)
   * After processing, the predictions and analysis will be displayed as a dataframe available for download in CSV format


<!-- FILES -->
## Files

### Main Folders and Classes
    .
    ├── recordings         # Webcam Recordings
        └── audio          # Audio Recordings
        └── video          # Video Recordings
        └── av_output      # Combined AV Recordings (Hume API input)
    ├── packages           # Packages and modules required for software
    ├── results            # Predictions and Pattern Mining Results
        └── extracted_emotions.csv       # Predictions of Hume API
        └── aggregated_emotions.csv      # Aggregated and cleaned results
        └── extracted_sequence.txt       # Input sequence of emotions for Sequence Mining
        └── output_sequence.txt          # Output results of Sequence Mining
    ├── .env               # Required for Hume AI and OpenAI API Key
    ├── batchmain.py       # Main script for batch uploader
    ├── batchuploader.py   # Functions for batch uploader
    ├── requirements.txt   # List of packages or libraries to be installed
    ├── streammain.py      # Main script for Pedagogical Agent
    ├── VideoProcessor.py  # Handles Hume API calls and Webcam recordings
    └── spmf.jar           # Algorithms for Pattern Mining

<!-- USAGE -->
## Usage

1. Configure processing interval in `main.py`, changing the interval parameter

   (Currently facing bugs, interval can only be max 5 seconds for now)
   ```py
   video_processor  =  VideoProcessor(API_KEY, interval=5)
   ```
   
	
2. Run the `main.py` file in terminal:
   ```py
   python main.py
   ```

3. Allow access to Camera and the video feed should start
4. While the video feed is running, emotion predictions (via the Hume API) will be printed in the terminal and also saved into `extracted_emotions.csv` and `aggregated_emotions.csv`
5. Recordings will be saved at every fixed interval *(default 5 sec)* into the `/recordings/av_output` folder
6. Sequences will be extracted into `extracted_sequence.txt` and encoded using Emotion IDs in `emotions_dict.py` 
7. To close the video feed, press 'Q' on your keyboard
8. Sequence mining algorithm will then run and output will be printed in `output_sequence.txt`



<!-- Recordings -->
## Recordings

AV Recordings will be saved in the `/recordings/av_output`  folder according to the interval set in `main.py`

Each clip is sent through an API call to Hume, returning predictions for emotion

### Prediction Results
#### Extracted Predictions
Prediction results from Hume are extracted into the `extracted_emotions.csv` file, along with the top 3 emotions and their prediction scores. The sequence of video IDs is also attached.
  ```json
{
	  "frame": 20,
	  "time": null,
	  "prob": 0.9996715784072876,
	  "face_id": "face_0",
	  "emotions": "[{'name': 'Disappointment', 'score': 0.36673504114151}, {'name': 'Sadness', 'score': 0.3661433458328247}]",  
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
Results are then aggregated into `aggregated_emotions.csv` which identifies the emotion with highest prediction score (~confidence), and the most frequently shown emotion in each interval.
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
After the video feed is ended by pressing 'Q' on the keyboard, the Sequence Mining Algorithm will run and generate an output `output_sequence.txt` that shows the most frequently occuring emotion sequence

  ```
  Example Output:
  
Boredom | #SUP: 50
Boredom | Boredom | #SUP: 47
Boredom | Boredom | Boredom | #SUP: 39
Boredom | Boredom | Boredom | Boredom | #SUP: 27
   ```

`|` represents the divider between item sets
`#SUP` indicates the support of the pattern in the dataset

# Decisions made during script development (~hyperparameters) 

### Hume 
- #### When combining Audio and Video, FFmpeg cuts off AV recording at 5s mark
   - Combined Video and Audio recording is limited to 5s recording to fit into Hume API's limit
   - Audio & Video recordings are separately recorded and saved at 5 seconds intervals
- #### When extracting emotion results from multiple Hume API models (e.g., Face, Prosody), emotion with highest average confidence across these models is selected
   - Example: In this prediction, the emotions will be averaged and the highest score will be extracted
      <table>
         <tr>
            <th>FaceModel</th>
            <td>Anger: 0.6 <br> Boredom: 0.2 <br> Confusion: 0.8 </td>
         </tr>
         <tr>
            <th>ProsodyModel</th>
            <td>Anger: 0.4 <br> Boredom: 0.4 <br> Confusion: 0.7 </td>
         </tr>
         <tr>
            <th>Averaged Emotions</th>
            <td>Anger: 0.5 <br> Boredom: 0.3 <br> Confusion: 0.75 </td>
         </tr>
      </table>

   - Confusion will be the most dominant emotion with an average score of 0.75


### Video Recording
- #### Audio file is saved first before incrementing naming id and subsequently saving Video file. More details below.
   - To save Audio file:
      - We use `self.audio.write_audio_file(output_name)`
      - A file of name `output_name` will be saved
   - To save Video file:
      - We use `out = self.webcam.write_video_file(output_name)`
      - This saves a video with file name from the previous `output_name` assigned when video was saved
      - A new video file of file name equal to the new `output_name` will be created for recording the future frames
   - So if we used the same `output_name` for saving both audio and video there would be issues syncing the files. To overcome this issue:
      - We first save audio file
      - Increment the `output_id`
      - Then save the video file
      - If not, video file id will lag behind audio file id by 1

# Error Troubleshooting
### SSLCertVerificationError
Update SSL certificate with certifi (MacOS only)
- Press "Command ⌘ + Space" button to open Spotlight
- type `Install Certificates.command`

[Credits](https://support.chainstack.com/hc/en-us/articles/9117198436249-Common-SSL-Issues-on-Python-and-How-to-Fix-it#:~:text=5.%20Update%20SSL%20certificate%20with%20certifi%20(MacOS%20only))


# Resources

- [Hume API Documentation](https://dev.hume.ai/docs/introduction)
- [SPMF Algorithms](https://www.philippe-fournier-viger.com/spmf/index.php?link=algorithms.php)
- [OpenAI Quickstart](https://platform.openai.com/docs/quickstart?context=python)
- [OpenAI Streaming](https://platform.openai.com/docs/api-reference/introduction?lang=python)


# Development
For development of the pedagogical agent, these are the key files to take note of:

### Batch Uploader
Allows user to upload a video or audio file for processing of emotions
- *`batchmain.py`*
   - Streamlit interface for *`batchuploader.py`*
- *`batchuploader.py`*
   - Functions for uploading of video or audio file
- *`packages/batchsplitter/ffmpeg-split.py`*
   - Currently not implemented
   - Splits the input file into smaller batches

### Pedagogical Agent
- *`VideoProcessor.py`*
   - Functions for processing of Webcam and Microphone into Video and Audio
- *`streammain.py`*
   - Main file to run for the Pedagogical Agent

### Hume
- *`packages/hume/Hume.py`*
   - API calls to Hume for processing of emotions
   - Aggregation of emotions' confidence scores
   - Saving of results file
   - Extracting of sequences of emotions, utility and frequency for SPMF algorithms (Not fully implemented)
   - Mapping of emotions to a numeric ID for SPMF algorithms

### GPT Connection
- *`packages/pipeline/gpt.py`*
   - Connection to the LLM model responsible for generating responses
   - Message history
   - Get examples for emotions-responses (Few Shot)
   - Stages for Agent prompts (Not yet implemented)
   - Flask connection to the Front End

### Pattern Mining (Not fully implemented)
- Currently not included in the response generation of the pedagogical agent, but some of the algorithms have been implemented
- *`packages/emotionpattern/emotions_dict.py`*
   - ID Mapping of Emotions to a numeric ID
   - Used in `Hume.py`
- *`packages/emotionpattern/PatternMine.py`*
   - Run a specified SPMF algorithm
