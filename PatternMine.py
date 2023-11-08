# Resource
# https://data-mining.philippe-fournier-viger.com/tutorial-how-to-call-spmf-from-python/

import os
import pandas as pd

class PatternMine:
    def __init__(self, algorithm="PrefixSpan", minsup=0.7, minpat=10):
        self.algorithm = algorithm
        self.minsup = minsup
        self.minpat = minpat    

    def run(self, input_filename, output_filename):
        # Run PrefixSpan algorithm from the command line, then writes to output file
        os.system(f"java -jar spmf.jar run {self.algorithm} {input_filename} {output_filename} {self.minsup} {self.minpat}")

        # return pd.read_csv("{output_filename}", header=None, sep= "-1")

    def print_results(self, file_name):
        # Read the output file line by line
        outFile = open(file_name,'r', encoding='utf-8')
        for string in outFile:
            print(string)
        outFile.close()


# pattern = PatternMine("PrefixSpan", 0.7, 5)
# pattern.run("contextPrefixSpan.txt", "output.txt")