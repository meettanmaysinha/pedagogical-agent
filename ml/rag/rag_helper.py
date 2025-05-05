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
    """Process PDFs, extract text, split into chunks, and store with library metadata."""

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=256,
        chunk_overlap=24,
        length_function=count_tokens,
    )

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)

            # Extract library name from filename (e.g., "numpy.pdf" → "numpy")
            library_name = file_name.replace(".pdf", "").lower()

            text = read_pdf(file_path)

            # Split the text into chunks
            chunks = text_splitter.create_documents([text])
            chunks = [chunk.page_content for chunk in chunks]

            print(f"Processed {file_name}: {len(chunks)} chunks")

            # Store with metadata
            vectors = embedding_fn.encode_documents(chunks)

            data = [
                {"id": i, "vector": vectors[i], "text": chunks[i], "metadata": {"library": library_name}}
                for i in range(len(vectors))
            ]

            print("Data has", len(data), "entities, each with fields: ", data[0].keys())
            print("Vector dim:", len(data[0]["vector"]))

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
    """Searches for relevant context and filters by library metadata."""

    # Library keyword mappings
    library_keywords = {
        "pandas": ["pd", "dataframe", "df", "iloc", "loc", "series", "groupby", "merge", "concat", "pivot", "melt"],
        "numpy": ["np", "array", "ndarray", "linspace", "arange", "zeros", "ones", "random", "linalg", "fft"],
        "matplotlib": ["plt", "pyplot", "figure", "subplot", "plot", "scatter", "hist", "bar", "boxplot", "imshow"],
        "sklearn": ["scikit", "scikit-learn", "classifier", "regressor", "cluster", "pipeline", "grid_search", "cross_val", "metrics", "fit", "predict", "train_test_split"],
        "scipy": ["stats", "interpolate", "optimize", "signal", "sparse", "spatial", "integrate", "ode"],
        "pytorch": ["torch", "nn", "optim", "cuda", "tensor", "autograd", "module", "dataloader", "dataset"],
        "tensorflow": ["tf", "keras", "estimator", "layers", "variable", "session", "model.fit", "sequential", "dense", "gpu"]
    }

    # query_vectors = embedding_fn.encode_documents(queries)
    query_vectors = embedding_fn.encode(queries)

    res = client.search(
        collection_name=collection_name,
        data=query_vectors,
        limit=5,
        output_fields=output_field,
    )

    # print(f'Res: {res}')

    # Extract the target library from the query
    query_text = " ".join(queries).lower()
    detected_libraries = set()

    # Check for direct library mentions
    relevant_libraries = list(library_keywords.keys())
    for lib in relevant_libraries:
        if lib in query_text:
            detected_libraries.add(lib)

    # Check for keyword matches
    for lib, keywords in library_keywords.items():
        for keyword in keywords:
            # Check for whole word matches to avoid partial matches
            if re.search(r'\b' + re.escape(keyword) + r'\b', query_text):
                detected_libraries.add(lib)
                break

    filtered_results = []

    for table in res[0]:
        if table["distance"] < distance_threshold:
            retrieved_library = table.get("entity", {}).get("metadata", {}).get("library", "").lower()

            # Include results if they match any detected library
            if detected_libraries and retrieved_library in detected_libraries:
                filtered_results.append(table["entity"]["text"])

    return filtered_results if filtered_results else []