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

# Import hashlib for PDF hash
import hashlib


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

# Calculate similarity between two embeddings
def cosine_similarity(question_embedding, chunk_embedding):
    dot_product = sum(
        x * y
        for x, y in zip(question_embedding, chunk_embedding)
    )

    magnitude_question = sum(
        x * x for x in question_embedding
    ) ** 0.5

    magnitude_chunk = sum(
        y * y for y in chunk_embedding
    ) ** 0.5

    return dot_product / (magnitude_question * magnitude_chunk)


# Find the most relevant chunks
def find_relevant_chunks(question, chunks, chunk_embeddings, top_k=3):
    question_embedding = create_embedding(question)

    scored_chunks = []

    for chunk, chunk_embedding in zip(chunks, chunk_embeddings):
        score = cosine_similarity(
            question_embedding,
            chunk_embedding
        )

        scored_chunks.append((score, chunk))

    scored_chunks.sort(
        reverse=True,
        key=lambda item: item[0]
    )

    top_chunks = scored_chunks[:top_k]

    return top_chunks


# Load summary from file
def load_summary(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Save summary to file
def save_summary(summary, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(summary)


# Summarize PDF text using AI
def summarize_text(text, language="th"):
    if language == "en":
        language_instruction = "Write the summary in English."
    else:
        language_instruction = "Write the summary in Thai."

    response = client.responses.create(
        model="gpt-5-mini",
        input=f"""
Create a detailed study summary of the following PDF content.

Requirements:
- Cover all major topics and important sections found in the document.
- Explain important concepts, definitions, and key ideas clearly.
- Preserve important examples, facts, and relationships when useful.
- Organize the summary with clear headings and bullet points.
- Make the level of detail proportional to the amount of content.
- Do not make the summary overly short.
- Do not add information that is not supported by the PDF.
- Do not add follow-up offers such as "If you want, I can..."
- Focus only on producing useful study notes.

{language_instruction}

PDF content:
{text}
"""
    )

    return response.output_text


# Load PDF hash from file
def load_pdf_hash(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()


# Save PDF hash
def save_pdf_hash(pdf_hash, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(pdf_hash)


# Create SHA-256 hash from PDF file
def create_pdf_hash(pdf_path):
    hasher = hashlib.sha256()

    with open(pdf_path, "rb") as file:
        while True:
            chunk = file.read(8192)

            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()


# Answer questions based on PDF content
def ask_question(text, question, language="th"):
    if language == "en":
        language_instruction = (
            "Answer entirely in English. "
            "Do not use Thai or any other language in the answer, "
            "even if the PDF contains text in another language. "
            "Translate relevant information into English."
        )
    else:   
        language_instruction = (
            "Answer entirely in Thai. "
            "Do not switch to another language unless a technical term "
            "must remain in its original form."
        )
    response = client.responses.create(
        model="gpt-5-mini",
        input=f"""
Answer the question using only the PDF content below.
If the information is not found in the PDF, say that the information was not found in the document.

{language_instruction}

PDF content:
{text}

Question:
{question}
""" 
    )

    return response.output_text