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
            {"role":"system","content":"You are a programming teacher, skilled in explaining complex programming concepts without divulging answers. Guide the students towards the answer, helping them with errors in their code."},
            {"role":"user","content":f"I am a student who is facing issues with my code: {cells_content}. For each error/output in 'output', the code snippet is in 'source'. I am feeling {emotions}. Encourage me and help me understand my problems better. Give me the code snippet in 'source' by quoting it"}
        ]
    )
    # print(completion.choices[0].message)

    return completion.choices[0].message.content
