# Retrieval Augmented Generation (RAG) Vector Database

This folder provides the implementation of a vector database for Retrieval Augmented Generation (RAG) using Milvus. RAG is an approach to enhance natural language generation models by retrieving relevant context from a vector database and augmenting prompts with that information. Documents to be indexed in the vector database should be placed in the /docs folder.

## Folder Structure and Key Files

1. db_set_up.py: Reads documents from the docs folder, tokenises them, and inserts the embeddings into the vector database. 
2. rag_serch.py: Contains the inner_product_search function, which performs similarity searches within the vectorbase to fetch the most relevant documents to the query vector.
3. prompt_helper.py: Implements the Prompt class, which manages prompt generation. This includes functions to format prompts based on a predefined template and query the inference endpoint.


## Set up

1. Install dependencies
```
pip install -r requirements.txt
```
2. Launch Milvus with Docker
```
docker-compose up -d
```

3. Set up the database 
```
python db_set_up.py
```

## Key Considerations

### Why Milvus
Milvus was chosen primarily due to:
1. Its ability to support high-speed similarity searches (handles up to 1700 queries per second)
2. Open-source and free-to-use, making it highly cost-effective
3. Flexibility for self-hosting or cloud deployment, which allows for easily scaling
4. Offers built-in support for numerous similarity metrics and indexing methods

### Embedding Model 

