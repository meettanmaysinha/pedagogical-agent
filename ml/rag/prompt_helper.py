from rag_search import ip_search
from dotenv import load_dotenv
import os
import requests
load_dotenv()
TEXT_TO_PYTHON_API_URL = os.getenv("TEXT_TO_PYTHON_API_URL")
HF_TOKEN = os.getenv("HF_TOKEN")

class Prompt:
    def __init__(self,prompt_file):
        self.prompt_file = prompt_file
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        }

    def generate_prompt(self,question):
        """
        Generates a prompt by reading a template file and formatting it with the user's question.
        Retrieves additional context through ip_search and appends it to the prompt.
        """
        with open(self.prompt_file, "r", encoding="utf-8") as file:
            prompt = file.read()
        prompt = prompt.format(user_question=question)
        res = ip_search([question],['text'],"collection_demo")
        #for i in range(len(res)):
            #res[i] = res[i].replace("\n", " ")
        return prompt + "\n".join(res)

    def query(self, question, api_url=TEXT_TO_PYTHON_API_URL):
        """
        Sends the generated prompt to the inference endpoint.
        """
        final_prompt = self.generate_prompt(question)
        
        payload = {
            "inputs": final_prompt,
            "parameters": {"return_full_text": False, "max_new_tokens": 600},
        }

        response = requests.post(api_url, headers=self.headers, json=payload, timeout=60)
        return response.json()

    


#prompt = Prompt("prompt.md")
#result = prompt.query("Problem: I am facing this error. numpy not defined, how to resolve?")
#print(result)


