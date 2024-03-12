from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY')
)

def get_chat_response(cells_content, emotions):
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"You are a programming teacher, skilled in explaining complex programming concepts with creative flair without divulging answers"},
            {"role":"user","content":f"I am a student who is facing issues with my code: {cells_content}. I am feeling {emotions}. Can you encourage me and help me understand my problems better?"}
        ]
    )
    print(completion.choices[0].message)

    return completion.choices[0].message
