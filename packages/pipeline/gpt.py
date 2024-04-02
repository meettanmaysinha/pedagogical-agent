from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import subprocess

# import nltk
# nltk.download('punkt')  # Download the punkt tokenizer models if not already downloaded

# from nltk.tokenize import word_tokenize

# Load the environment variables
load_dotenv()

# Initialise the OpenAI API
openai = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY')
)

# Function to start Flask for the Agent API endpoint
def run_agent_api():
    subprocess.Popen("python packages/pipeline/gpt.py", shell=True)

# Initialise Flask
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define the API endpoint for the chat response
@app.route('/api/chat', methods=['POST'])
def api_get_chat_response():
    """
    API endpoint to get a chat response.

    This endpoint accepts a POST request with JSON data containing 'cells_content'
    and returns a response based on the provided content.

    Parameters:
        - cells_content (str): Extracted cell content from Jupyter Notebook.
        - emotions (str): Emotions expressed by the user.

    Returns:
        JSON: A JSON response containing the chat response.

    Example usage:
        ```
        POST /api/chat
        {
            "cells_content": "Your Jupyter Notebook content here"
        }
        ```

    If any required parameters are missing, it returns a JSON response with an error message.
    """
    if request.method == 'POST':
        data = request.json  # Assuming the data is sent in JSON format
        cells_content = data.get('cells_content')
        emotions = get_emotions()
        print(cells_content)
        print(emotions)
        if cells_content is None or emotions is None:
            return jsonify({"error": "Missing required parameters"}), 400

        response = get_chat_response(cells_content, emotions)

        return jsonify({"response": response}), 200

def get_chat_response(cells_content, emotions):
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"You are a programming teacher, skilled in explaining complex programming concepts without divulging answers. Guide the students towards the answer, helping them with errors in their code."},
            {"role":"user","content": "I am a student who is facing issues with my code." \
            f"Here is my extracted cell content from Jupyter Notebook: {cells_content}."\
            "For each error/output in output, the code snippet is in source. " \
            f"My emotion is: {emotions}. Help me understand my problems better." \
            "Give me the error code snippet in source by quoting it." \
            "Do not explicitly mention the dataset given to you, but you may mention its values."}
        ],
        # logit_bias = {word_tokenize("dataset")[0]: -1,},
    )

    return completion.choices[0].message.content

def get_emotions():
    aggregated_emotions = pd.read_csv("./results/aggregated_emotions.csv")
    student_emotions = aggregated_emotions[["occurring_emotions", "datetime"]]
    return student_emotions.iloc[-1, 0]

if __name__ == '__main__':
    port = 8000 # Default port set to 8000
    try:
        app.run(port=port, debug=True)
    except OSError as e:
        print("Port is already in use, please kill the process and try again.")
        print("You can kill the process using the following command in the terminal:")
        print("npx kill-port 8000")