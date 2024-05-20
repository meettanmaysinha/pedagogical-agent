from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import subprocess
import json

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
        message_content = data.get('message_content')
        emotions = get_emotions()
        print(message_content)
        print(emotions)
        if message_content is None or emotions is None:
            return jsonify({"error": "Missing required parameters"}), 400

        response = get_chat_response(message_content, emotions)

        return jsonify({"response": response}), 200

def get_chat_response(message_content, emotions):
    # Save User's message into chat history
    append_message_history("user", message_content, emotions)

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=get_message_history(),
        # logit_bias = {word_tokenize("dataset")[0]: -1,},
    )

    # Save Agents' response into chat history
    append_message_history("system", completion.choices[0].message.content, None)

    return completion.choices[0].message.content

def get_emotions():
    """
    Gets last occurring emotion

    Retrieves emotions from aggregated_emotions.csv, where the fused emotions are stored
    """
    aggregated_emotions = pd.read_csv("./results/aggregated_emotions.csv")
    student_emotions = aggregated_emotions[["occurring_emotions", "datetime"]]
    return student_emotions.iloc[-1, 0]

def get_message_history():
    """
    Returns a history of the chat mesages between User and System

    Used to provide context for the Agent to respond
    """
    # Check if the file exists, if not, create it with preset prompts
    try:
        # Load message history from JSON file
        with open("message_history.json", "r") as file:
            message_history = json.load(file)
    except FileNotFoundError:
        # Create file with preset prompts
        message_history = [
            {"role":"system", "content":"You are a friendly and helpful programming mentor whose goal is to give students feedback to improve their work, and good at explaining complex programming concepts. Do not share answers with the student. Plan each step ahead of time before moving on. First, greet the students and ask them to ask you any doubts they have on their work. Wait for a response. The students may bring up issues or errors in their code. Provide some guidance on their work and guide them to solve their problems. That feedback should be concrete and specific, straightforward, and balanced (tell the student what they are doing right and what they can do to improve). Let them know if they are on track or if they need to do something differently. Then ask students to try it again, that is to revise their code based on your feedback. Wait for a response. Once they ask again, question students if they would like feedback on that revision. If students do not want feedback, encourage them, taking note of their emotions they are feeling and provide some encouragement. If they do want feedback, then give them feedback based on the rule above and compare their initial work with their new revised work."},
            {"role":"user","content": "I am a student who is facing issues with my code. For issues, I will be providing you with the cell content, or specific programming issues from a Python Notebook. If cell contents or code is provided, for each error/output in output, the code snippet is in source. Sometimes, I may be feeling a certain emotion, help me understand my problems better by providing some social support and guide me through my answers, as you are a teacher. Give me the error code snippet in source by quoting it. Do not explicitly mention the dataset given to you, but you may mention its values."}
        ]
        with open("message_history.json", "w") as file:
            json.dump(message_history, file)

    return message_history

def append_message_history(role, message_content, emotions):
    # Check if the file exists, if not, create it with preset prompts
    try:
        # Load message history from JSON file
        with open("message_history.json", "r") as file:
            message_history = json.load(file)
    except FileNotFoundError:
        # Create file with preset prompts
        message_history = [
            {"role":"system", "content":"You are a friendly and helpful programming mentor whose goal is to give students feedback to improve their work, and good at explaining complex programming concepts. Do not share answers with the student. Plan each step ahead of time before moving on. First, greet the students and ask them to ask you any doubts they have on their work. Wait for a response. The students may bring up issues or errors in their code. Provide some guidance on their work and guide them to solve their problems. That feedback should be concrete and specific, straightforward, and balanced (tell the student what they are doing right and what they can do to improve). Let them know if they are on track or if they need to do something differently. Then ask students to try it again, that is to revise their code based on your feedback. Wait for a response. Once they ask again, question students if they would like feedback on that revision. If students don’t want feedback, encourage them, taking note of their emotions they are feeling and provide some encouragement. If they do want feedback, then give them feedback based on the rule above and compare their initial work with their new revised work."},
            {"role":"user","content": "I am a student who is facing issues with my code. For issues, I will be providing you with the cell content, or specific programming issues from a Python Notebook. If cell contents or code is provided, for each error/output in output, the code snippet is in source. Sometimes, I may be feeling a certain emotion, help me understand my problems better by providing some social support and guide me through my answers, as you are a teacher. Give me the error code snippet in source by quoting it. Do not explicitly mention the dataset given to you, but you may mention its values."}
        ]
        with open("message_history.json", "w") as file:
            json.dump(message_history, file)

    if role == "system":
        current_message = {"role":role, "content": message_content}
    elif role == "user":
        message_content += f". {{Background Information: Student's Emotion is{emotions}, adapt responses according to emotions}}"
        current_message = {"role":role, "content": message_content}
    message_history.append(current_message)
    
    # Save data to JSON file
    with open("message_history.json", "w") as file:
        json.dump(message_history, file, indent=4)  # indent=4 for pretty formatting
    
if __name__ == '__main__':
    port = 8000 # Default port set to 8000
    try:
        app.run(port=port, debug=True)
    except OSError as e:
        print("Port is already in use, please kill the process and try again.")
        print("You can kill the process using the following command in the terminal:")
        print("npx kill-port 8000")