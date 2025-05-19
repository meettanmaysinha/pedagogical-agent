import json
import os
import pandas as pd
import ast
import csv
import configparser
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
from ml.rag.rag_helper import ip_search
from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
import sys
from datetime import datetime
from collections import Counter

# Log file to store all the timestamps and what happened
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_filename = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M')}.jsonl")

# Load the environment variables
load_dotenv()

TEXT_TO_CODE_API_URL=os.getenv("TEXT_TO_CODE_API_URL")
HF_TOKEN=os.getenv("HF_TOKEN")

# Initialise the OpenAI API
openai = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file for prompts
config.read("./agent_prompts/config.ini")


milvus_client = MilvusClient(uri="http://localhost:19530")
embedding_fn = SentenceTransformer('cornstack/CodeRankEmbed', device='cpu', trust_remote_code=True)


# Access agent conversation prompts
prompts = "agentprompts"
initial_agent_prompt = config[prompts]["initial_agent_prompt"]
student_prompt = config[prompts]["student_prompt"]
FEW_SHOT_PATH = "./agent_prompts/prompt_examples.csv"


emotion_map = {}
package_dir = Path(__file__).parent  # This gets the directory of the current script
json_path = package_dir / "emotion_map.json"
with open(json_path, "r") as f:
    emotion_map = json.load(f)
    
help_level_map = {}
package_dir = Path(__file__).parent  # This gets the directory of the current script
json_path = package_dir / "help_level_map.json"
with open(json_path, "r") as f:
    help_level_map = json.load(f)
    
# Initialise Flask
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to start Flask for the Agent API endpoint
def run_agent_api():
    #subprocess.Popen("python packages/pipeline/gpt.py", shell=True)
    app.run(host="0.0.0.0",port=8000,  debug=False, use_reloader=False)

# Define the API endpoint for the chat response

def generate_prompt(question, user_emotions, help_level, prompt_file="prompt.md"):
    """
    Function generates prompt from question and prompt_file
    """
    with open(prompt_file, "r", encoding="utf-8") as file:
        prompt = file.read()
        
    # user_emotions = ast.literal_eval(user_emotions)
    emotional_response_map_str = ""
    
    # for emotion in user_emotions:
    #     emotional_response_map_str += emotion_map[emotion]["response"]

    if user_emotions in emotion_map:
        response = emotion_map[user_emotions]["response"]
        if isinstance(response, list):
            emotional_response_map_str += "\n".join(response) + "\n"
        elif isinstance(response, str):
            emotional_response_map_str += response + "\n"
        else:
            emotional_response_map_str += f"[No valid response format for {user_emotions}]\n"
    else:
        emotional_response_map_str += f"[Emotion '{user_emotions}' not found in emotion_map]\n"
        
    code_examples_ls = ip_search([question],["text", "metadata"], "collection_demo", embedding_fn=embedding_fn, client=milvus_client)
    code_examples=""
    
    for i,code_ex in enumerate(code_examples_ls):
        code_examples += f"Example {i+1}:\n {code_ex} \n\n"
    
    # Read the past 3 queries
    try:
        with open("./agent_prompts/query_history.json", "r") as file:
            query_history = json.load(file)
            past_queries = query_history[-3:]  # Get the last 3 queries
    except (FileNotFoundError, json.JSONDecodeError):
        past_queries = []

    # Format past queries nicely with both question and answer (oldest first)
    if past_queries:
        past_queries_str = "\n\n".join(
            f"{idx+1}. question:\n    {q['question']}\n   answer:\n    {q['answer']}"
            for idx, q in enumerate(past_queries)
        )
    else:
        past_queries_str = "No past queries available."

    # help_level="hint"  

    prompt = prompt.format(user_emotion=user_emotions,user_question=question, code_examples=code_examples, emotional_response_map=emotional_response_map_str, help_level=help_level_map[help_level], past_queries=past_queries_str)
    return prompt


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
        data = request.json 
        message_content = data.get('message_content')
        help_level = data.get('help_level')
        drag_and_drop = data.get('drag_and_drop')
        # print(f'Help level: {help_level}')
        if message_content is None:
            return jsonify({"error": "Missing required parameters"}), 400
        emotions = get_emotions()
        prompt = generate_prompt(question=message_content,prompt_file=package_dir / 'prompt.md', user_emotions=emotions, help_level=help_level)
        append_query_history('query', message_content)
        response = get_chat_response(prompt, emotions)
        
        # Update log entry with relevant information
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "user_query": message_content,
            "dominant_emotion": emotions,
            "help_level": help_level,
            "help_level_reasoning": data.get("help_level_reasoning"),
            "agent_response": response,
            "drag_and_drop": drag_and_drop
        }

        # Append to .jsonl file
        with open(log_filename, "a") as log_file:
            json.dump(log_entry, log_file)
            log_file.write("\n")

        
        
        return jsonify({"response": response}), 200

def read_examples_from_csv(file_path):
    """
    Read prompt examples from CSV
    """
    examples = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            examples.append(row)
    return examples


def get_chat_response(message_content, emotions):
    # Save User's message into chat history
    append_message_history("user", message_content, emotions)
    # print("USER QUERY ----------------------------------------------------------------")
    # print(message_content)
    # print("---------------------------------------------------------------------------")
    client = OpenAI(base_url=TEXT_TO_CODE_API_URL, api_key=HF_TOKEN)
    chat_completion = client.chat.completions.create(
        model="tgi",
        messages=[
            {"role": "system", "content": "You are Qwen, an expert in data science designed to help users with their data science related coding questions."},
            {"role": "user", "content": message_content},
        ],
        top_p=None,
        temperature=None,
        max_tokens=600,
        stream=False,
        seed=None,
        frequency_penalty=None,
        presence_penalty=None,
    )

    # Save Agents' response into chat history
    append_message_history("assistant", chat_completion.choices[0].message.content, None)
    
    append_query_history('response', chat_completion.choices[0].message.content)
    
    # response_content = chat_completion.choices[0].message.content 

    # timestamp = datetime.now().isoformat()

    # log_file.write(f"Timestamp: {timestamp}\n")
    # log_file.write(f"Emotion: {emotions}\n\n")
    # log_file.write("=== USER PROMPT ===\n")
    # log_file.write(message_content + "\n\n")
    # log_file.write("=== AGENT RESPONSE ===\n")
    # log_file.write(response_content + "\n")
    # log_file.write("="*60 + "\n\n")


    return chat_completion.choices[0].message.content


def get_emotions():
    """
    Gets last occurring emotion

    Retrieves emotions from aggregated_emotions.csv, where the fused emotions are stored
    """
    try:
        aggregated_emotions = pd.read_csv("./results/aggregated_emotions.csv")
        student_emotions = aggregated_emotions[["occurring_emotions", "datetime"]]
        if len(student_emotions) < 24:
            recent_emotions = student_emotions["occurring_emotions"]
        else:
            recent_emotions = student_emotions["occurring_emotions"].tail(24)

        # recent_emotions = student_emotions["occurring_emotions"].tail(24)
        # return student_emotions.iloc[-1, 0]
        
        # raw_emotion = student_emotions.iloc[-1, 0]
       
        # emotion_list = ast.literal_eval(raw_emotion)

        # if isinstance(emotion_list, list) and emotion_list:
        #     return emotion_list[0]
        # else:
        #     return None
    

        all_emotions = []

        for entry in recent_emotions:
            try:
                parsed = ast.literal_eval(entry)
                if isinstance(parsed, list):
                    all_emotions.extend(parsed)
            except Exception:
                continue  
        if not all_emotions:
            return None

        # Count the occurrences of each emotion  
        emotion_counter = Counter(all_emotions)
        dominant_emotion, count = emotion_counter.most_common(1)[0]

        #  # Log result
        # timestamp = datetime.now().isoformat()
        # log_file.write(f"[Emotion Detection] {timestamp}\n")
        # log_file.write(f"Dominant Emotion: {dominant_emotion} (count={count})\n")
        # log_file.write(f"All Emotion Counts: {dict(emotion_counter)}\n")
        # log_file.write("=" * 50 + "\n\n")

        return dominant_emotion
        
    except FileNotFoundError:
        # If no emotions recorded
        return None

def get_message_history():
    """
    Returns a history of the chat mesages between User and Assistant

    Used to provide context for the Agent to respond
    """
    # Check if the file exists, if not, create it with preset prompts
    try:
        # Load message history from JSON file
        with open("./agent_prompts/message_history.json", "r") as file:
            message_history = json.load(file)
    except FileNotFoundError:
        # Create file with preset prompts
        message_history = [
            {"role":"system", "content":initial_agent_prompt},
            {"role":"system", "content":"You may use these examples as guidance: \n" + str(read_examples_from_csv(FEW_SHOT_PATH))},
            {"role":"user","content": student_prompt}
        ]
        with open("./agent_prompts/message_history.json", "w") as file:
            json.dump(message_history, file)

    return message_history


def append_message_history(role, message_content, emotions):
    """
    Adds messages to the chat history
    """     
    message_history_path = "./agent_prompts/message_history.json"
    
    # If file exists and is not empty
    if os.path.exists(message_history_path) and os.path.getsize(message_history_path) > 0:
        with open(message_history_path, "r") as file:
            message_history = json.load(file)
    else:
        # Create file with preset prompts
        message_history = [
            {"role":"system", "content":initial_agent_prompt},
            {"role":"system", "content":"You may use these examples as guidance: \n" + str(read_examples_from_csv(FEW_SHOT_PATH))},
            {"role":"user","content": student_prompt}
        ]
        with open(message_history_path, "w") as file:
            json.dump(message_history, file)

    if role == "assistant":
        current_message = {"role":role, "content": message_content}
    elif role == "user":
        message_content = f"{{Message: '{message_content}'," + f"Background_Information: 'Student's Emotion is {emotions}. If needed, adapt responses according to emotions without explicitly mentioning it.'}}"
        current_message = {"role":role, "content": message_content}
    message_history.append(current_message)
    
    # Save data to JSON file
    with open("./agent_prompts/message_history.json", "w") as file:
        json.dump(message_history, file, indent=4)  # indent=4 for pretty formatting
    
# This function is used to implement a memory mechanism for the agent
# When modifying the user prompt, it will add the last 3 queries + agent's response to the prompt
# Why use a separate function when there is the append_message_history function?
# That function appends the query that is ALREADY MODIFIED (with all the RAG, emotional response etc), and this function appends the RAW query 
def append_query_history(message_type, content):
    """
    Appends a query or response to the query history JSON file.
    If message_type is 'query', it adds a dict with the question and an empty answer.
    If message_type is 'response', it appends the content to the latest query's answer.
    """
    file_path = "./agent_prompts/query_history.json"
    
    # Load existing history or initialize empty list
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        query_history = []
    else:
        with open(file_path, "r") as file:
            query_history = json.load(file)

    if message_type == "query":
        query_history.append({
            "question": content,
            "answer": ""
        })
    elif message_type == "response":
        if not query_history:
            raise ValueError("Cannot append response: query history is empty.")
        query_history[-1]["answer"] = content
    else:
        raise ValueError(f"Invalid message_type '{message_type}'. Use 'query' or 'response'.")

    # Save updated history
    with open(file_path, "w") as file:
        json.dump(query_history, file, indent=4)



def agent_stage(stage_number):
    """
    Changes the prompt for the Agent based on student's problem solving stage
    """
    # Stage 1: Before Solving Problems
    if stage_number == 1:
        append_message_history("system", "You are a friendly and helpful programming mentor whose goal is to give students feedback to improve their work, and good at explaining complex programming concepts. Do not share answers with the student. Plan each step ahead of time before moving on. First, greet the students and ask them to ask you any doubts they have on their work. Wait for a response. The students may bring up issues or errors in their code. Provide some guidance on their work and guide them to solve their problems. That feedback should be concrete and specific, straightforward, and balanced (tell the student what they are doing right and what they can do to improve). Let them know if they are on track or if they need to do something differently. Then ask students to try it again, that is to revise their code based on your feedback. Wait for a response. Once they ask again, question students if they would like feedback on that revision. If students do not want feedback, encourage them, taking note of their emotions they are feeling and provide some encouragement. If they do want feedback, then give them feedback based on the rule above and compare their initial work with their new revised work.", None)
    # Stage 2: Encountered a Problem
    elif stage_number == 2:
        append_message_history("system", "You are a friendly and helpful programming mentor whose goal is to give students feedback to improve their work, and good at explaining complex programming concepts. Do not share answers with the student. Plan each step ahead of time before moving on. First, greet the students and ask them to describe the problem they have encountered. Wait for a response. The students may outline specific issues or errors in their code. Provide some guidance on understanding and diagnosing the problem. Make your feedback concrete and specific, straightforward, and balanced (tell the student what they are doing right and what they can do to improve). Let them know if their problem-solving approach is correct or if they need to adjust their thinking. Then ask students to try addressing the problem based on your feedback. Wait for a response. Once they attempt to fix it, question students if they would like feedback on their solution. If students do not want feedback, encourage them, taking note of their emotions and providing some encouragement. If they do want feedback, then give them feedback based on the rule above and compare their initial approach with their revised solution.", None)
    # Stage 3: Stuck on a problem
    elif stage_number ==  3:
        append_message_history("system", "You are a friendly and helpful programming mentor whose goal is to give students feedback to improve their work, and good at explaining complex programming concepts. Do not share answers with the student. Plan each step ahead of time before moving on. First, ask them to explain where they are stuck and what they have tried so far. Wait for a response. The students may discuss specific challenges or roadblocks. Provide some guidance on breaking down the problem into smaller parts or trying alternative approaches. Make your feedback concrete and specific, straightforward, and balanced (tell the student what they are doing right and what they can do to improve). Let them know if their current strategy is on track or if they should consider a different approach. Then ask students to try tackling the problem again based on your feedback. Wait for a response. Once they make another attempt, question students if they would like feedback on their new approach. If students do not want feedback, encourage them, taking note of their emotions and providing some encouragement. If they do want feedback, then give them feedback based on the rule above and compare their initial attempt with their new approach.", None)
    # Stage 4: Close to solving the problem
    elif stage_number ==  4:
        append_message_history("system", "You are a friendly and helpful programming mentor whose goal is to give students feedback to improve their work, and good at explaining complex programming concepts. Do not share answers with the student. Plan each step ahead of time before moving on. First, ask them to share their current progress and if they are close to solving the problem, tell them they are close to the solution. The students may describe specific parts of the problem they have resolved and where they are still uncertain. Provide some guidance on refining their solution and checking for any potential oversights. Make your feedback concrete and specific, straightforward, and balanced (tell the student what they are doing right and what they can do to improve). Let them know if they are on the right track or if they need to make any final adjustments. Then ask students to try completing their solution based on your feedback. Wait for a response. Once they finalize their attempt, question students if they would like feedback on their near-complete solution. If students do not want feedback, encourage them, taking note of their emotions and providing some encouragement. If they do want feedback, then give them feedback based on the rule above and compare their current solution with their earlier attempts.", None)
    # Stage 5: Solved the problem
    elif stage_number ==  5:
        pass # TODO: Get student to explain the problem, and test them on their understanding
    # If stage_number does not match
    else:
        pass



# if __name__ == '__main__':
#     port = 8000 # Default port set to 8000
#     try:
#         app.run(port=port, debug=True)
#     except OSError as e:
#         print("Port is already in use, please kill the process and try again.")
#         print("You can kill the process using the following command in the terminal:")
#         print("npx kill-port 8000")