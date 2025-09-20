# In backend/qa_engine.py

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load a pre-trained model. This will be downloaded from the internet on the first run.
# It's a small but powerful model perfect for this task.
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_index(structured_content: list):
    """
    Creates a FAISS index from the extracted paragraphs.
    """
    # We only want to index the paragraphs for Q&A.
    paragraphs = [item['text'] for item in structured_content if item['type'] == 'para']
    
    if not paragraphs:
        print("No paragraphs found to index.")
        return None, None
        
    print(f"Encoding {len(paragraphs)} paragraphs into vectors...")
    embeddings = model.encode(paragraphs, convert_to_numpy=True)
    
    # The dimension of our vectors.
    embedding_dimension = embeddings.shape[1]
    
    # Create a FAISS index. IndexFlatL2 is a basic but fast index for L2 distance.
    index = faiss.IndexFlatL2(embedding_dimension)
    index.add(embeddings)
    
    print("FAISS index created successfully.")
    return index, paragraphs

def answer_question(question: str, index, source_paragraphs: list):
    """
    Finds the most relevant paragraphs from the source text for a given question.
    """
    if not index or not source_paragraphs:
        return "The document has not been indexed or contains no paragraphs."

    # Encode the user's question into a vector.
    question_vector = model.encode([question], convert_to_numpy=True)
    
    # Search the index for the top 3 most similar paragraphs.
    k = 3 
    distances, indices = index.search(question_vector, k)
    
    # Retrieve the original text of the most relevant paragraphs.
    results = [source_paragraphs[i] for i in indices[0] if i < len(source_paragraphs)]
    
    # Combine the results into a single context string.
    context = " ".join(results)
    return context