from pymilvus import MilvusClient
from pymilvus import model

client = MilvusClient(uri="http://localhost:19530")
DISTANCE_THRESHOLD = 0.30

embedding_fn = model.DefaultEmbeddingFunction()

"""
embedding_fn =  model.dense.SentenceTransformerEmbeddingFunction(
    model_name='jinaai/jina-embeddings-v2-base-en', # Specify the model name
    device='cpu' # Specify the device to use, e.g., 'cpu' or 'cuda:0'
)
"""


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
        collection_name=collection_name,  # target collection
        data=query_vectors,  # query vectors
        limit=3,  # number of returned entities
        output_fields=output_field,  # specifies fields to be returned
    
    )
    res = [table['entity']['text'] for table in res[0] if table["distance"] > DISTANCE_THRESHOLD]
    
    return res

#res = ip_search(["Problem: In order to get a numpy array from a list I make the following: Suppose n = 12 np.array([i for i in range(0, n)]) And get: array([ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]) Then I would like to make a (4,3) matrix from this array: np.array([i for i in range(0, 12)]).reshape(4, 3) and I get the following matrix: array([[ 0, 1, 2], [ 3, 4, 5], [ 6, 7, 8], [ 9, 10, 11]]) But if I know that I will have 3 * n elements in the initial list how can I reshape my numpy array, because the following code np.array([i for i in range(0,12)]).reshape(a.shape[0]/3,3) Results in the error TypeError: 'float' object cannot be interpreted as an integer A: <code> import numpy as np a = np.arange(12) </code> a = ... # put solution in this variable BEGIN SOLUTION <code>"], ["text"], "collection_demo")
