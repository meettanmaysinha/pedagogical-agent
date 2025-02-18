from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
import pandas as pd
import ast
import csv
import configparser
from ml.rag.rag_helper import ip_search
from pymilvus import MilvusClient, model


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
embedding_fn =  model.dense.SentenceTransformerEmbeddingFunction(
    model_name='cornstack/CodeRankEmbed',
    device='cpu',
    trust_remote_code=True  
)

# Access agent conversation prompts
prompts = "agentprompts"
initial_agent_prompt = config[prompts]["initial_agent_prompt"]
student_prompt = config[prompts]["student_prompt"]
FEW_SHOT_PATH = "./agent_prompts/prompt_examples.csv"



emotion_map = {
'Anxious': 	'A student is feeling anxious about an upcoming exam.	"1. **Acknowledge the feeling:** \I understand that exams can be really stressful. It is normal to feel anxious.\""\n2. **Offer reassurance:** \""Remember, you have been preparing for this. Trust in your preparation.\""\n3. **Provide practical advice:** \""Would you like some tips on how to manage your study time or practice some relaxation techniques?\""\n4. **Encourage:** \""You got this! Take one step at a time and focus on doing your best.\""',

'Excited':	'A student is excitedly sharing news about winning a science fair.	"1. **Acknowledge the excitement:** \""That is amazing! Congratulations on winning the science fair!\""\n2. **Encourage sharing:** \""Can you tell me more about your project? I would love to hear all the details.\""\n3. **Reinforce positive feelings:** \""It is clear you put a lot of hard work into this, and it paid off. Great job!\""\n4. **Channel the energy:** \""Maybe you can inspire your classmates by sharing your experience and what you learned from it.\"""',

'Angry':	'A student is angry after receiving a lower grade than expected on an assignment.	"1. **Acknowledge the anger:** \""I can see you are upset about your grade. It is okay to feel that way.\""\n2. **Encourage expression:** \""Would you like to talk about what specifically is bothering you about the grade?\""\n3. **Provide constructive advice:** \""Lets review your assignment together and see where there might be areas for improvement.\""\n4. **Support positive action:** \""Remember, one grade doesnt define your abilities. Use this as a learning opportunity to do even better next time.\"""',

'Sad':	'A student is feeling sad due to a recent personal issue.	"1. **Show empathy:** \""I am sorry to hear that you are feeling sad. It is important to take care of yourself.\""\n2. **Offer support:** \""Would you like some suggestions on how to cope with these feelings, or do you just need someone to listen?\""\n3. **Provide resources:** \""Here are some resources that might help you manage your emotions. Remember, it is okay to reach out for help.\""\n4. **Encourage self-care:** \""Make sure to take some time for yourself and do things that make you feel better.\"""',

'Frustrated':	'A student is frustrated with a difficult homework problem.	"1. **Acknowledge the frustration:** \""It sounds like this problem is really challenging. That is completely understandable.\""\n2. **Offer reassurance:** \""It is okay to feel frustrated. Difficult problems can often be the most rewarding to solve.\""\n3. **Provide step-by-step help:** \""Lets break down the problem together and tackle it one step at a time. Where do you think you are getting stuck?\""\n4. **Encourage persistence:** \""You are doing great by not giving up. Keep trying, and lets see how we can solve this together.\"""',

'Confused':	'A student is confused about the instructions for a project.	"1. **Acknowledge the confusion:** \""I can see how these instructions might be confusing.\""\n2. **Clarify the instructions:** \""Lets go through the instructions together. Here is what each part means.\""\n3. **Provide examples:** \""Would you like to see an example of a completed project to help understand better?\""\n4. **Encourage questions:** \""Feel free to ask any questions you have. I am here to help you understand.\"""',

'Bored':	'A student is expressing boredom with the current lesson.	"1. **Acknowledge the feeling:** \""I understand that you might find this lesson a bit boring.\""\n2. **Engage interest:** \""What part of the subject do you find most interesting? Maybe we can focus on that.\""\n3. **Offer alternatives:** \""Would you like to try a different approach or activity related to this topic?\""\n4. **Encourage exploration:** \""Sometimes exploring the topic in a different way can make it more exciting. Lets find a way that works for you.\"""',

'Curious':	'A student is curious about a topic not covered in the curriculum.	"1. **Encourage curiosity:** \""It is great that you are curious about this topic!\""\n2. **Provide information:** \""Here is some information to get you started on this topic.\""\n3. **Suggest further exploration:** \""Would you like some recommendations for books, articles, or videos on this subject?\""\n4. **Support learning:** \""Feel free to ask more questions as you explore. I am here to help you learn more about anything you are interested in.\"""',

'Disappointed':	'A student is disappointed after not making the school sports team.	"1. **Acknowledge the disappointment:** \""Its completely normal to feel disappointed about not making the team.\""\n2. **Provide empathy:** \""I amm sorry to hear that. You worked hard, and it is tough when things dont go as planned.\""\n3. **Encourage resilience:** \""Remember, this is just one setback. There are many other opportunities to come.\""\n4. **Suggest alternatives:** \""Maybe you can try out for another team or focus on improving your skills for next time.\""',

'Motivated':	'A student is highly motivated and eager to learn more about a subject.	"1. **Recognize the motivation:** \""Its fantastic to see you so motivated and eager to learn!\""\n2. **Provide resources:** \""Here are some advanced materials and resources you can explore.\""\n3. **Encourage deeper learning:** \""Would you like to work on a special project related to this subject?\""\n4. **Support continued interest:** \""Keep up the great work! Your enthusiasm is inspiring.\""',

'Concentration':	'A student is currently concentrated in their work.	Allow student to continue working on their own.',

'Amusement': 'A student is amused by the work. Encourage their passion by quizzing them.',
'Interest': 'A student is amused by the work. Encourage their interest by recommeding them extra content.',
}

# Initialise Flask
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to start Flask for the Agent API endpoint
def run_agent_api():
    #subprocess.Popen("python packages/pipeline/gpt.py", shell=True)
    app.run(host="0.0.0.0",port=8000, debug=True)

# Define the API endpoint for the chat response

def generate_prompt(question, user_emotions, prompt_file="prompt.md"):
    """
    Function generates prompt from question and prompt_file
    """
    with open(prompt_file, "r", encoding="utf-8") as file:
        prompt = file.read()
    user_emotions = ast.literal_eval(user_emotions)
    emotional_response_map_str = ""
    for emotion in user_emotions:
        emotional_response_map_str += emotion_map[emotion]
    code_examples_ls = ip_search([question],["text"], "collection_demo", embedding_fn=embedding_fn, client=milvus_client)
    code_examples=""
    for i,code_ex in enumerate(code_examples_ls):
        code_examples += f"Example {i+1}:\n {code_ex} \n\n"
    prompt = prompt.format(user_emotion=" and ".join(user_emotions),user_question=question, code_examples=code_examples, emotional_response_map=emotional_response_map_str)
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
        if message_content is None:
            return jsonify({"error": "Missing required parameters"}), 400
        emotions = get_emotions()
        prompt = generate_prompt(question=message_content,prompt_file='/Users/nickyloo/projects/ra_job/pedagogical-agent/packages/pipeline/prompt.md', user_emotions=emotions)
        print("PROMPT",prompt)
        response = get_chat_response(prompt, emotions)
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
    
    client = OpenAI(base_url=TEXT_TO_CODE_API_URL, api_key=HF_TOKEN)

    chat_completion = client.chat.completions.create(
        model="tgi",
        messages=[
            {"role": "system", "content": "You are Qwen, an expert in data science designed to help users with their data science related coding questions."},
            {"role": "user", "content": message_content},
        ],
        top_p=None,
        temperature=None,
        max_tokens=150,
        stream=False,
        seed=None,
        frequency_penalty=None,
        presence_penalty=None,
    )

    # Save Agents' response into chat history
    append_message_history("assistant", chat_completion.choices[0].message.content, None)

    return chat_completion.choices[0].message.content

def get_emotions():
    """
    Gets last occurring emotion

    Retrieves emotions from aggregated_emotions.csv, where the fused emotions are stored
    """
    try:
        aggregated_emotions = pd.read_csv("./results/aggregated_emotions.csv")
        student_emotions = aggregated_emotions[["occurring_emotions", "datetime"]]
        return student_emotions.iloc[-1, 0]
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

    if role == "assistant":
        current_message = {"role":role, "content": message_content}
    elif role == "user":
        message_content = f"{{Message: '{message_content}'," + f"Background_Information: 'Student's Emotion is {emotions}. If needed, adapt responses according to emotions without explicitly mentioning it.'}}"
        current_message = {"role":role, "content": message_content}
    message_history.append(current_message)
    
    # Save data to JSON file
    with open("./agent_prompts/message_history.json", "w") as file:
        json.dump(message_history, file, indent=4)  # indent=4 for pretty formatting
    
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



if __name__ == '__main__':
    port = 8000 # Default port set to 8000
    try:
        app.run(port=port, debug=True)
    except OSError as e:
        print("Port is already in use, please kill the process and try again.")
        print("You can kill the process using the following command in the terminal:")
        print("npx kill-port 8000")