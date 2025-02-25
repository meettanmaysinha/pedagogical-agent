from pymilvus import MilvusClient, model
from transformers import GPT2TokenizerFast
from rag_helper import process_pdfs_in_folder

try:
    client = MilvusClient(uri="http://localhost:19530")
    print("Connected successfully!")
except Exception as e:
    print("Connection failed:", e)


if client.has_collection(collection_name="collection_demo"):
    client.drop_collection(collection_name="collection_demo")

client.create_collection(
    collection_name="collection_demo",
    dimension=768,  
)
embedding_fn =  model.dense.SentenceTransformerEmbeddingFunction(
    model_name='cornstack/CodeRankEmbed',
    device='cpu', # Specify the device to use, e.g., 'cpu' or 'cuda:0'
    trust_remote_code=True  
)


tokenizer_gpt = GPT2TokenizerFast.from_pretrained("gpt2")


process_pdfs_in_folder("./docs", client=client, embedding_fn=embedding_fn)



