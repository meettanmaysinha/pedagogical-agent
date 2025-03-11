## Introduction

This foldercontains the necessary code to evaluate the DS-1000 dataset using our Qwen2.5-Coder-7B-Instruct LLM model. The goal is to assess the model's performance on data science-related tasks and measure its competencies in generating accurate and relevant outputs.

## Folder Structure and Key Files

1. /data: Contains the inference results of each model on the DS-1000 dataset.
2. /result: Contains the evalution result for each model.
3. run_inference.py: Contains the code to run inference on the DS-1000 dataset. Output will be stored in the /data folder
4. test_ds1000.py: Evaluates model by executing testcases against the outputs in the /data folder. Results will be stored in /result
5. qwen_evaluation_notebook.ipynb: A Jupyter Notebook providing an example of performing the DS-1000 evaluation on the model.
6. qwen_rag_inference_notebook.ipynb: A Jupyter Notebook providing an example of performing the DS-1000 inference, with RAG on the model.

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

# Changelog

## Original DS-1000 Evaluation Results

### Score Summary

|       | score |
| ----- | ----- |
| count | 1000  |
| mean  | 0.378 |

### Score by Library

| Library    | Count | Mean  |
| ---------- | ----- | ----- |
| Matplotlib | 155   | 0.626 |
| Numpy      | 220   | 0.345 |
| Pandas     | 291   | 0.333 |
| Pytorch    | 68    | 0.338 |
| Scipy      | 106   | 0.236 |
| Sklearn    | 115   | 0.365 |
| Tensorflow | 45    | 0.400 |

### Score by Perturbation Type

| Perturbation Type | Count | Mean  |
| ----------------- | ----- | ----- |
| Difficult-Rewrite | 162   | 0.198 |
| Origin            | 452   | 0.476 |
| Semantic          | 234   | 0.385 |
| Surface           | 152   | 0.270 |

<br />
<br />

## March 5, 2025

<br />

- Added functions to read from website and csv files (read_csv currently not in use)
- Added keyword matching to ip_search
  - When cheatsheets are inserted into the milvus db, they now contain the library name in metadata
- Improved the prompts for the ds1000 evaluation

### Score Summary

|       | score |
| ----- | ----- |
| count | 1000  |
| mean  | 0.427 |

### Score by Library

| Library    | Count | Mean  |
| ---------- | ----- | ----- |
| Matplotlib | 155   | 0.665 |
| Numpy      | 220   | 0.523 |
| Pandas     | 291   | 0.323 |
| Pytorch    | 68    | 0.426 |
| Scipy      | 106   | 0.425 |
| Sklearn    | 115   | 0.270 |
| Tensorflow | 45    | 0.222 |

### Score by Perturbation Type

| Perturbation Type | Count | Mean  |
| ----------------- | ----- | ----- |
| Difficult-Rewrite | 162   | 0.265 |
| Origin            | 452   | 0.531 |
| Semantic          | 234   | 0.423 |
| Surface           | 152   | 0.296 |
