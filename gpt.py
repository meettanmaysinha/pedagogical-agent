from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY')
)

def get_chat_response():
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"You are a programming teacher, skilled in explaining complex programming concepts with creative flair without divulging answers"},
            {"role":"user","content":"I am a student who is struggling to understand the concept of recursion in programming. Can you help me understand it better?"}
        ]
    )
    print(completion.choices[0].message)

    return completion.choices[0].message
