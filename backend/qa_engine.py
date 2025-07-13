import openai
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os

# Use a small, fast model for local embedding
EMBED_MODEL = 'all-MiniLM-L6-v2'
model = SentenceTransformer(EMBED_MODEL)

# Helper: embed a list of texts
def embed_texts(texts):
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

# Build FAISS index for a list of chunks
def build_faiss_index(chunks):
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embed_texts(texts)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, texts, embeddings

# Retrieve top-k relevant chunks
def retrieve_chunks(question, chunks, index, texts, embeddings, k=3):
    q_emb = embed_texts([question])
    D, I = index.search(q_emb, k)
    results = []
    for idx in I[0]:
        results.append(chunks[idx])
    return results

# Generate answer using OpenAI (RAG)
def answer_question(question, doc_chunks):
    # Build index
    index, texts, embeddings = build_faiss_index(doc_chunks)
    # Retrieve top chunks
    top_chunks = retrieve_chunks(question, doc_chunks, index, texts, embeddings, k=3)
    # Compose context
    context = "\n---\n".join([c['text'] for c in top_chunks])
    prompt = f"Answer the following question using ONLY the provided context. Cite the most relevant snippet and its location.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer (with snippet and location):"
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a careful assistant. Only answer using the provided context. Always cite the snippet and its location (page/paragraph)."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.2
    )
    answer = response.choices[0].message.content.strip()
    # For UI: also return the top evidence chunk and its location
    evidence = top_chunks[0]['text']
    pages = top_chunks[0].get('pages', [])
    paragraphs = top_chunks[0].get('paragraphs', [])
    location = f"Pages: {pages}, Paragraphs: {paragraphs}"
    return answer, evidence, location
