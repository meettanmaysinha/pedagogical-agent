## Introduction

This foldercontains the necessary code to evaluate the DS-1000 dataset using our Qwen2.5-Coder-7B-Instruct LLM model. The goal is to assess the model's performance on data science-related tasks and measure its competencies in generating accurate and relevant outputs.

## Folder Structure and Key Files

1. /data: Contains the inference results of each model on the DS-1000 dataset.
2. /result: Contains the evalution result for each model.
3. run_inference.py: Contains the code to run inference on the DS-1000 dataset. Output will be stored in the /data folder
4. test_ds1000.py: Evaluates model by executing testcases against the outputs in the /data folder. Results will be stored in /result
5. QwenEvaluation.ipynb: A Jupyter Notebook providing an example of performing inference and evaluation on the model.


## Set up evaluatiob

1. Create and activate conda environment
```
conda env create -f environment.yml
conda activate ds1000-3.10

```
2. Run test script
```
python test_ds1000.py
```


## Key Considerations

### Why DS-1000
DS-1000 was chosen as our evaluation metric because:
1. Relevance to Data Science: The dataset is specifically tailored to assess competencies in data science, making it more applicable for our evaluations.
2. Execution-Based Metrics: It employs execution-based metrics that provide a more accurate assessment of the model's performance, incorporating surface form constraints to enforce good programming practices.
3. Greater Context: DS-1000 features a larger number of average problem words, providing richer context for evaluation.
4. Real-World Problem Representation: The data is sourced from real-world platforms (Stack Overflow), reflecting how people commonly ask questions and seek solutions, ensuring the evaluation is grounded in practical scenarios.



### Acknowledgements

This project makes use of the evaluation metric implementation by Lai, Yuhang and Li, Chengxi and Wang, Yiming and Zhang, Tianyi and Zhong, Ruiqi and Zettlemoyer, Luke and Yih, Wen-Tau and Fried, Daniel and Wang, Sida and Yu, Tao (https://github.com/xlang-ai/DS-1000). Thank you for your valuable contribution to the community!


