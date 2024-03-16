import json 
import pandas as pd

def extract_cells(nb_file_name):
    with open(nb_file_name, mode= "r", encoding= "utf-8") as f:
        myfile = json.loads(f.read())

    # converting json dataset from dictionary to dataframe
    nb_content = pd.json_normalize(myfile["cells"])
    nb_content["output"] = pd.json_normalize(nb_content["outputs"])
    return nb_content