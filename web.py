# Import FastAPI and file upload tools
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request


# Import session middleware
from starlette.middleware.sessions import SessionMiddleware


# Import template tools
from fastapi.templating import Jinja2Templates


# Import static file tools
from fastapi.staticfiles import StaticFiles


# Import Path for file paths
from pathlib import Path


# Import database functions
from database import (
    create_user,
    get_user_by_login,
    get_document_by_hash,
    get_documents_by_user,
    get_document_by_id,
    create_document
)


# Import authentication functions
from auth import hash_password, verify_password


# Import MySQL error
from mysql.connector import IntegrityError


# Import operating system tools
import os


# Import hashing tools
import hashlib


# Import function from another file
from rag import (
    extract_text_from_pdf,
    split_text,
    load_pdf_hash,
    load_embeddings,
    create_chunk_embeddings,
    save_embeddings,
    load_summary,
    summarize_text,
    save_summary,
    save_pdf_hash,
    find_relevant_chunks,
    ask_question,
)


# Import BaseModel for request data
from pydantic import BaseModel


# Import environment tools
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Create FastAPI application
app = FastAPI()


# Add session support
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY")
)


# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# HTML templates
templates = Jinja2Templates(directory="templates")


# Folder for uploaded PDF files
DATA_DIR = Path("data")


# Make sure the data folder exists
DATA_DIR.mkdir(exist_ok=True)


# Request model for PDF questions
class QuestionRequest(BaseModel):
    question: str
    language: str = "th"


# Request model for user registration
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


# Request model for user login
class LoginRequest(BaseModel):
    login: str
    password: str


# Home page
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# Register a new user
@app.post("/register")
def register_user(request: RegisterRequest):

    # Check that all fields are filled
    if (
        not request.username.strip()
        or not request.email.strip()
        or not request.password
    ):
        raise HTTPException(
            status_code=400,
            detail="All fields are required"
        )

    # Check password length
    if len(request.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )

    # Hash password before saving
    password_hash = hash_password(request.password)

    try:
        user_id = create_user(
            request.username.strip(),
            request.email.strip(),
            password_hash
        )

    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    return {
        "message": "User registered successfully",
        "user_id": user_id,
        "username": request.username
    }


# Log in a user
@app.post("/login")
def login_user(data: LoginRequest, request: Request):

    # Check that all fields are filled
    if not data.login.strip() or not data.password:
        raise HTTPException(
            status_code=400,
            detail="All fields are required"
        )

    # Find user in database
    user = get_user_by_login(data.login.strip())

    # Check username or email
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username/email or password"
        )

    # Check password
    if not verify_password(
        data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username/email or password"
        )

    # Store user data in session
    request.session["user_id"] = user["id"]
    request.session["username"] = user["username"]
    request.session["email"] = user["email"]

    return {
        "message": "Login successful",
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"]
    }


# Get the currently logged-in user
@app.get("/me")
def get_current_user(request: Request):

    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Not logged in"
        )

    return {
        "user_id": user_id,
        "username": request.session.get("username"),
        "email": request.session.get("email")
    }


# Get documents owned by the current user
@app.get("/documents")
def get_user_documents(request: Request):

    # Get logged-in user ID
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Please log in first"
        )

    # Get documents from database
    documents = get_documents_by_user(user_id)

    return {
        "documents": documents
    }


# Select a document for the current user
@app.post("/documents/{document_id}/select")
def select_document(
    document_id: int,
    request: Request,
    language: str = "th"
):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not logged in."
        )

    document = get_document_by_id(
        user_id,
        document_id
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    request.session["current_document_id"] = document_id

    pdf_path = Path(document["file_path"])
    summary_path = Path("data") / (
        pdf_path.stem + f"_summary_{language}.txt"
    )

    summary = ""

    if summary_path.exists():
        summary = load_summary(summary_path)

    else:
        pdf_text = extract_text_from_pdf(pdf_path)

        summary = summarize_text(
            pdf_text,
            language
        )

        save_summary(
            summary,
            summary_path
        )

    return {
        "message": "Document selected.",
        "document_id": document_id,
        "filename": document["filename"],
        "summary": summary
    }


# Log out the current user
@app.post("/logout")
def logout_user(request: Request):

    request.session.clear()

    return {
        "message": "Logout successful"
    }


# Upload PDF route
@app.post("/upload")
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form("th")
):

    # Check that the user is logged in
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Please log in first"
        )

    # Check that the uploaded file is a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
    
    # Read uploaded file
    file_content = await file.read()

    # Create PDF hash from uploaded content
    pdf_hash = hashlib.sha256(file_content).hexdigest()

    # Check if this document already exists for the user
    existing_document = get_document_by_hash(
        user_id,
        pdf_hash
    )

    # Use the existing path if the document already exists
    if existing_document is not None:
        file_path = Path(existing_document["file_path"])
        document_filename = existing_document["filename"]

    else:
        # Keep only the file name for safety
        safe_filename = Path(file.filename).name

        # Create a unique stored file name
        stored_filename = (
            f"user_{user_id}_"
            f"{pdf_hash[:16]}_"
            f"{safe_filename}"
        )

        file_path = DATA_DIR / stored_filename
        document_filename = safe_filename

    # Get PDF name without extension
    pdf_name = file_path.stem

    # Create cache file paths
    embeddings_path = DATA_DIR / f"{pdf_name}_embeddings.json"
    summary_path = DATA_DIR / f"{pdf_name}_summary_{language}.txt"
    hash_path = DATA_DIR / f"{pdf_name}_hash.txt"

    # Save uploaded file
    with open(file_path, "wb") as saved_file:
        saved_file.write(file_content)

    # Extract text from uploaded PDF
    pdf_text = extract_text_from_pdf(file_path)

    # Split extracted text into chunks
    chunks = split_text(pdf_text)

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
        summary = summarize_text(pdf_text, language)
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
        
    if existing_document is not None:
        document_id = existing_document["id"]

    else:
        # Save new document information to database
        document_id = create_document(
            user_id,
            document_filename,
            file_path,
            pdf_hash
        )

    # Store the uploaded document as the current document
    request.session["current_document_id"] = document_id

    return {
        "message": "PDF processed successfully",
        "document_id": document_id,
        "filename": document_filename,
        "text_length": len(pdf_text),
        "chunk_count": len(chunks),
        "summary": summary
    }

# Ask question route
@app.post("/ask")
def ask_pdf(data: QuestionRequest, request: Request):

    # Check that the user is logged in
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Please log in first"
        )

    # Get the selected document ID from the session
    document_id = request.session.get("current_document_id")

    if document_id is None:
        raise HTTPException(
            status_code=400,
            detail="Please upload or select a PDF first"
        )

    # Get the selected document and verify ownership
    document = get_document_by_id(
        user_id,
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Build the embeddings cache path
    file_path = Path(document["file_path"])
    pdf_name = file_path.stem
    embeddings_path = DATA_DIR / f"{pdf_name}_embeddings.json"

    # Load embeddings for the selected document
    if embeddings_path.exists():
        chunks, chunk_embeddings = load_embeddings(
            embeddings_path
        )

    else:
        # Rebuild embeddings if the cache is missing
        pdf_text = extract_text_from_pdf(file_path)
        chunks = split_text(pdf_text)

        chunk_embeddings = create_chunk_embeddings(chunks)

        save_embeddings(
            chunks,
            chunk_embeddings,
            embeddings_path
        )

    # Check that the question is not empty
    if not data.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    # Find relevant chunks
    relevant_chunks = find_relevant_chunks(
        data.question,
        chunks,
        chunk_embeddings
    )

    # Combine relevant chunks into context
    context = "\n\n".join(
        chunk for score, chunk in relevant_chunks
    )

    # Ask AI using relevant PDF context
    answer = ask_question(
        context,
        data.question,
        data.language
    )

    return {
        "question": data.question,
        "answer": answer
    }