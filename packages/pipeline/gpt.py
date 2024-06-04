from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import subprocess
import json

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
            "message_content": "Your message or Jupyter Notebook content here"
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
    )

    # Save Agents' response into chat history
    append_message_history("assistant", completion.choices[0].message.content, None)

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
    Returns a history of the chat mesages between User and Assistant

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
    """
    Adds messages to the chat history
    """
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

    if role == "assistant":
        current_message = {"role":role, "content": message_content}
    elif role == "user":
        message_content = f"{{Message: '{message_content}'," + f"Background_Information: 'Student's Emotion is {emotions}. If needed, adapt responses according to emotions without explicitly mentioning it.'}}"
        current_message = {"role":role, "content": message_content}
    message_history.append(current_message)
    
    # Save data to JSON file
    with open("message_history.json", "w") as file:
        json.dump(message_history, file, indent=4)  # indent=4 for pretty formatting
    
def agent_stage(stage_number):
    """
    Changes the prompt for the Agent based on student's problem solving stage
    """
    match stage_number:
        # Stage 1: Before Solving Problems
        case 1:
            append_message_history("system", "You are a friendly and helpful programming mentor whose goal is to give students feedback to improve their work, and good at explaining complex programming concepts. Do not share answers with the student. Plan each step ahead of time before moving on. First, greet the students and ask them to ask you any doubts they have on their work. Wait for a response. The students may bring up issues or errors in their code. Provide some guidance on their work and guide them to solve their problems. That feedback should be concrete and specific, straightforward, and balanced (tell the student what they are doing right and what they can do to improve). Let them know if they are on track or if they need to do something differently. Then ask students to try it again, that is to revise their code based on your feedback. Wait for a response. Once they ask again, question students if they would like feedback on that revision. If students do not want feedback, encourage them, taking note of their emotions they are feeling and provide some encouragement. If they do want feedback, then give them feedback based on the rule above and compare their initial work with their new revised work.", None)
        # Stage 2: Encountered a Problem
        case 2:
            append_message_history("system", "You are a friendly and helpful programming mentor whose goal is to give students feedback to improve their work, and good at explaining complex programming concepts. Do not share answers with the student. Plan each step ahead of time before moving on. First, greet the students and ask them to describe the problem they have encountered. Wait for a response. The students may outline specific issues or errors in their code. Provide some guidance on understanding and diagnosing the problem. Make your feedback concrete and specific, straightforward, and balanced (tell the student what they are doing right and what they can do to improve). Let them know if their problem-solving approach is correct or if they need to adjust their thinking. Then ask students to try addressing the problem based on your feedback. Wait for a response. Once they attempt to fix it, question students if they would like feedback on their solution. If students do not want feedback, encourage them, taking note of their emotions and providing some encouragement. If they do want feedback, then give them feedback based on the rule above and compare their initial approach with their revised solution.", None)
        # Stage 3: Stuck on a problem
        case 3:
            append_message_history("system", "You are a friendly and helpful programming mentor whose goal is to give students feedback to improve their work, and good at explaining complex programming concepts. Do not share answers with the student. Plan each step ahead of time before moving on. First, ask them to explain where they are stuck and what they have tried so far. Wait for a response. The students may discuss specific challenges or roadblocks. Provide some guidance on breaking down the problem into smaller parts or trying alternative approaches. Make your feedback concrete and specific, straightforward, and balanced (tell the student what they are doing right and what they can do to improve). Let them know if their current strategy is on track or if they should consider a different approach. Then ask students to try tackling the problem again based on your feedback. Wait for a response. Once they make another attempt, question students if they would like feedback on their new approach. If students do not want feedback, encourage them, taking note of their emotions and providing some encouragement. If they do want feedback, then give them feedback based on the rule above and compare their initial attempt with their new approach.", None)
        # Stage 4: Close to solving the problem
        case 4:
            append_message_history("system", "You are a friendly and helpful programming mentor whose goal is to give students feedback to improve their work, and good at explaining complex programming concepts. Do not share answers with the student. Plan each step ahead of time before moving on. First, ask them to share their current progress and if they are close to solving the problem, tell them they are close to the solution. The students may describe specific parts of the problem they have resolved and where they are still uncertain. Provide some guidance on refining their solution and checking for any potential oversights. Make your feedback concrete and specific, straightforward, and balanced (tell the student what they are doing right and what they can do to improve). Let them know if they are on the right track or if they need to make any final adjustments. Then ask students to try completing their solution based on your feedback. Wait for a response. Once they finalize their attempt, question students if they would like feedback on their near-complete solution. If students do not want feedback, encourage them, taking note of their emotions and providing some encouragement. If they do want feedback, then give them feedback based on the rule above and compare their current solution with their earlier attempts.", None)
        # If stage_number does not match
        case _:
            pass

if __name__ == '__main__':
    port = 8000 # Default port set to 8000
    try:
        app.run(port=port, debug=True)
    except OSError as e:
        print("Port is already in use, please kill the process and try again.")
        print("You can kill the process using the following command in the terminal:")
        print("npx kill-port 8000")