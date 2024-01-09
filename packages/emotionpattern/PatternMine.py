# Resources
# https://data-mining.philippe-fournier-viger.com/tutorial-how-to-call-spmf-from-python/

# Documentation
# https://www.philippe-fournier-viger.com/spmf/PrefixSpan.php

import os
import subprocess
import pandas as pd
from . import emotions_dict

class PatternMine:
    def __init__(self, algorithm="PrefixSpan", minsup=0.7, minpat=10):
        self.algorithm = algorithm
        self.minsup = minsup
        self.minpat = minpat    


    def run(self, input_filename, output_filename):
        # Read existing content
        with open('extracted_sequence.txt', 'r') as f:
            existing_content = f.read()

        # Write new content along with existing content
        with open('extracted_sequence.txt', 'w') as f:
            # Write the Emotions decoder to the file
            f.write(emotions_dict.emotions_sequence_map)
            # Write the existing content back to the file
            f.write(existing_content)

        # Run PrefixSpan algorithm from the command line, then writes to output file
        subprocess.call(f"java -jar spmf.jar run {self.algorithm} {input_filename} {output_filename} {self.minsup} {self.minpat}", shell=True)


    def print_results(self, file_name):
        # Read the output file line by line
        outFile = open(file_name,'r', encoding='utf-8')
        for string in outFile:
            print(string)
        outFile.close()


# pattern = PatternMine("PrefixSpan", 0.7, 5)
# pattern.run("contextPrefixSpan.txt", "output.txt")

