# Import FastAPI and file upload tools
from fastapi import FastAPI, UploadFile, File, HTTPException


# Import Path for file paths
from pathlib import Path


# Import function from another file
from rag import extract_text_from_pdf, split_text


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

    # Read uploaded file
    file_content = await file.read()

    # Save uploaded file
    with open(file_path, "wb") as saved_file:
        saved_file.write(file_content)

    # Extract text from uploaded PDF
    pdf_text = extract_text_from_pdf(file_path)

    # Split extracted text into chunks
    chunks = split_text(pdf_text)
    
    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename,
        "text_length": len(pdf_text),
        "chunk_count": len(chunks)
    }