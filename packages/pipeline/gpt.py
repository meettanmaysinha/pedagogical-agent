from openai import OpenAI
from dotenv import load_dotenv
import os
# import nltk
# nltk.download('punkt')  # Download the punkt tokenizer models if not already downloaded

# from nltk.tokenize import word_tokenize

load_dotenv()


openai = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY')
)

def get_chat_response(cells_content, emotions):
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"You are a programming teacher, skilled in explaining complex programming concepts without divulging answers. Guide the students towards the answer, helping them with errors in their code."},
            {"role":"user","content": "I am a student who is facing issues with my code." \
             f"Here is my extracted cell content from Jupyter Notebook: {cells_content}."\
             "For each error/output in output, the code snippet is in source. " \
             f"I am feeling {emotions}. Help me understand my problems better." \
             "Give me the error code snippet in source by quoting it." \
             "Do not explicitly mention the dataset given to you, but you may mention its values."}
        ],
        # logit_bias = {word_tokenize("dataset")[0]: -1,},

    )
    # print(completion.choices[0].message)

    return completion.choices[0].message.content
