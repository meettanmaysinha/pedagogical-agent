import re
import os
import fitz
from pymilvus import MilvusClient
from transformers import GPT2TokenizerFast
from langchain.text_splitter import RecursiveCharacterTextSplitter


DISTANCE_THRESHOLD = 0.25

tokenizer_gpt = GPT2TokenizerFast.from_pretrained("gpt2")

def count_tokens(text: str) -> int:
    return len(tokenizer_gpt.encode(text))

def read_pdf(file_path: str) -> str:
    """Extract text from the PDF file and return it as a single string."""
    text = ""
    with fitz.open(file_path) as pdf:
        for page_num in range(len(pdf)):
            page = pdf.load_page(page_num)
            text += page.get_text("text")  # Extract text from the page
    return text

def process_pdfs_in_folder(folder_path: str ,embedding_fn, client: MilvusClient, collection_name="collection_demo"):
    """Process pdf texts and insert into RAG database"""
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=256,  # Size of chunks (in tokens)
        chunk_overlap=24,  # Tokens overlap between chunks
        length_function=count_tokens,  # Function to count tokens in each chunk
    )

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            text = read_pdf(file_path)
            chunks = text_splitter.create_documents([text])
            chunks = [chunk.page_content for chunk in chunks]
            vectors = embedding_fn.encode_documents(chunks)
            data = [
                {"id": i, "vector": vectors[i], "text": chunks[i]} for i in range(len(vectors))
            ]
            res = client.insert(collection_name=collection_name, data=data)
            print(res)



def ip_search(
    queries,
    output_field,
    collection_name,
    embedding_fn,
    client: MilvusClient,
    distance_threshold=DISTANCE_THRESHOLD,
):
    """Function does an ip search, based on the parameters provided"""
    query_vectors = embedding_fn.encode_queries(queries)
    res = client.search(
        collection_name=collection_name,  
        data=query_vectors,  
        limit=3, 
        output_fields=output_field,  
    
    )
    
    res = [table['entity']['text'] for table in res[0] if table["distance"] > distance_threshold]
    return res