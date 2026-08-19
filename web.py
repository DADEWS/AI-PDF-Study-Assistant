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
    save_pdf_hash
)


# Create FastAPI application
app = FastAPI()


# Folder for uploaded PDF files
DATA_DIR = Path("data")


# Home route
@app.get("/")
def home():
    return {
        "message": "AI PDF Study Assistant"
    }


# Upload PDF route
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

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
        "message": "PDF uploaded successfully",
        "filename": file.filename,
        "text_length": len(pdf_text),
        "chunk_count": len(chunks),
        "pdf_hash": pdf_hash,
        "cache_valid": cache_valid,
        "embedding_count": len(chunk_embeddings),
        "summary_loaded": summary is not None
    }