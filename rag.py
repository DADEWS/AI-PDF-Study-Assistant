# Import PyMuPDF for PDF text extraction
import pymupdf


# Import environment tools
from dotenv import load_dotenv


# Import OpenAI client (embedding)
from openai import OpenAI


# Load environment variables from .env
load_dotenv()


# Create OpenAI client (embedding)
client = OpenAI()

# Import JSON for saving embedding data
import json


# Extract text from PDF 
def extract_text_from_pdf(pdf_path):
    document = pymupdf.open(pdf_path)

    text = ""

    for page in document:
        text += page.get_text("text", sort=True)

    document.close()

    return text

# Split text into smaller chunks
def split_text(text, chunk_size=1000, overlap=200):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]
        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks

# Create embedding from text
def create_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


# Create embeddings for all chunks
def create_chunk_embeddings(chunks):
    embeddings = []

    for chunk in chunks:
        embedding = create_embedding(chunk)
        embeddings.append(embedding)

    return embeddings


# Save chunks and embeddings to file
def save_embeddings(chunks, embeddings, file_path):
    data = []

    for chunk, embedding in zip(chunks, embeddings):
        data.append({
            "chunk": chunk,
            "embedding": embedding
        })

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)


# Load chunks and embeddings from file
def load_embeddings(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    chunks = []
    embeddings = []

    for item in data:
        chunks.append(item["chunk"])
        embeddings.append(item["embedding"])

    return chunks, embeddings