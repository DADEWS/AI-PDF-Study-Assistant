# Import FastAPI and file upload tools
from fastapi import FastAPI, UploadFile, File, HTTPException


# Import Path for file paths
from pathlib import Path


# Import function from another file
from rag import (
    extract_text_from_pdf,
    split_text,
    create_pdf_hash,
    load_pdf_hash,
    load_embeddings,
    create_chunk_embeddings,
    save_embeddings,
    load_summary,
    summarize_text,
    save_summary,
    save_pdf_hash,
    find_relevant_chunks,
    ask_question
)


# Import BaseModel for request data
from pydantic import BaseModel


# Create FastAPI application
app = FastAPI()


# Folder for uploaded PDF files
DATA_DIR = Path("data")


# Store data for the currently uploaded PDF
current_chunks = []
current_chunk_embeddings = []


# Request model for PDF questions
class QuestionRequest(BaseModel):
    question: str


# Home route
@app.get("/")
def home():
    return {
        "message": "AI PDF Study Assistant"
    }


# Upload PDF route
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    global current_chunks, current_chunk_embeddings

    # Check that the uploaded file is a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
    
    # Create destination file path
    file_path = DATA_DIR / file.filename

    # Get PDF name without extension
    pdf_name = file_path.stem

    # Create cache file paths
    embeddings_path = DATA_DIR / f"{pdf_name}_embeddings.json"
    summary_path = DATA_DIR / f"{pdf_name}_summary.txt"
    hash_path = DATA_DIR / f"{pdf_name}_hash.txt"

    # Read uploaded file
    file_content = await file.read()

    # Save uploaded file
    with open(file_path, "wb") as saved_file:
        saved_file.write(file_content)

    # Extract text from uploaded PDF
    pdf_text = extract_text_from_pdf(file_path)

    # Split extracted text into chunks
    chunks = split_text(pdf_text)

    # Create PDF hash
    pdf_hash = create_pdf_hash(file_path)

    # Check if cached PDF hash matches current PDF
    cache_valid = False

    if hash_path.exists():
        saved_hash = load_pdf_hash(hash_path)

        if saved_hash == pdf_hash:
            cache_valid = True

    # Load cached embeddings if cache is valid
    chunk_embeddings = []

    if cache_valid and embeddings_path.exists():
        chunks, chunk_embeddings = load_embeddings(embeddings_path)

    else:
        chunk_embeddings = create_chunk_embeddings(chunks)
        save_embeddings(
            chunks,
            chunk_embeddings,
            embeddings_path
        )

    # Store RAG data for question answering
    current_chunks = chunks
    current_chunk_embeddings = chunk_embeddings

    # Load cached summary if cache is valid
    summary = None

    if cache_valid and summary_path.exists():
        summary = load_summary(summary_path)

    else:
        summary = summarize_text(pdf_text)
        save_summary(
            summary,
            summary_path
        )

    # Save PDF hash after creating new cache
    if not cache_valid:
        save_pdf_hash(
            pdf_hash,
            hash_path
        )
    
    return {
        "message": "PDF processed successfully",
        "filename": file.filename,
        "text_length": len(pdf_text),
        "chunk_count": len(chunks),
        "summary": summary
    }


# Ask question route
@app.post("/ask")
def ask_pdf(request: QuestionRequest):

    # Check that a PDF has been uploaded
    if not current_chunks or not current_chunk_embeddings:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF first"
        )

    # Check that the question is not empty
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    # Find relevant chunks
    relevant_chunks = find_relevant_chunks(
        request.question,
        current_chunks,
        current_chunk_embeddings
    )

    # Combine relevant chunks into context
    context = "\n\n".join(
        chunk for score, chunk in relevant_chunks
    )

    # Ask AI using relevant PDF context
    answer = ask_question(
        context,
        request.question
    )

    return {
        "question": request.question,
        "answer": answer
    }