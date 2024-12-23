import re
from pymilvus import MilvusClient
from pymilvus import model


client = MilvusClient(uri="http://localhost:19530")


if client.has_collection(collection_name="collection_demo"):
    client.drop_collection(collection_name="collection_demo")

client.create_collection(
    collection_name="collection_demo",
    dimension=768,  # The vectors we will use in this demo has 768 dimensions
)
#embedding_fn = model.DefaultEmbeddingFunction()

embedding_fn =  model.dense.SentenceTransformerEmbeddingFunction(
    model_name='cornstack/CodeRankEmbed', # Specify the model name
    device='cpu', # Specify the device to use, e.g., 'cpu' or 'cuda:0'
    trust_remote_code=True  
)

with open("docs/numpy.txt", "r", encoding="utf-8") as file:
    text = file.read()
numpy_examples = [s for s in text.split('###') if s]
first_lines = [s.split('\n',1)[0] for s in numpy_examples]

vectors = embedding_fn.encode_documents(first_lines)

data = [
    {"id": i, "vector": vectors[i], "text": numpy_examples[i]} for i in range(len(vectors))
]
res = client.insert(collection_name="collection_demo", data=data)


