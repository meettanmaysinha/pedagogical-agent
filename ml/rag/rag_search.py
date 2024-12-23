from pymilvus import MilvusClient
from pymilvus import model

client = MilvusClient(uri="http://localhost:19530")
DISTANCE_THRESHOLD = 0.35

#embedding_fn = model.DefaultEmbeddingFunction()

embedding_fn =  model.dense.SentenceTransformerEmbeddingFunction(
    model_name='cornstack/CodeRankEmbed', # Specify the model name
    device='cpu', # Specify the device to use, e.g., 'cpu' or 'cuda:0'
    trust_remote_code=True  
)


def ip_search(
    queries,
    output_field,
    collection_name,
    distance_threshold=DISTANCE_THRESHOLD,
    embedding_fn=embedding_fn,
):
    """Function does an ip search, based on the parameters provided"""
    query_vectors = embedding_fn.encode_queries(queries)
    res = client.search(
        collection_name=collection_name,  
        data=query_vectors,  
        limit=5, 
        output_fields=output_field,  
    
    )
    
    res = [table['entity']['text'] for table in res[0] if table["distance"] > DISTANCE_THRESHOLD]
    return res