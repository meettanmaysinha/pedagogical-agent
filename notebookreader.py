import json 
import pandas as pd

with open("Pipeline Testing.ipynb", mode= "r", encoding= "utf-8") as f:
    myfile = json.loads(f.read())

# converting json dataset from dictionary to dataframe
nb_content = pd.json_normalize(myfile["cells"])
print(nb_content)