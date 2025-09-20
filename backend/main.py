# In backend/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import os

# Import your custom modules
from pdf_processor import extract_structured_text
from qa_engine import create_index, answer_question
from persona_layer import apply_persona

# Initialize the FastAPI app
app = FastAPI(title="PDF Q&A Backend")

# --- CORS (Cross-Origin Resource Sharing) Middleware ---
# This is crucial to allow your Next.js frontend (running on a different port)
# to make requests to this backend.
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-Memory Storage for Sessions ---
# This dictionary will hold the processed data for each uploaded PDF.
# The key is a unique session_id. The value is another dict
# containing the FAISS index and the list of paragraphs.
session_data = {}

# --- Pydantic model for the /ask request body ---
# This ensures that any request to the /ask endpoint has the correct data structure.
class AskRequest(BaseModel):
    session_id: str
    question: str
    persona: str

# --- API Endpoints ---

@app.get("/", tags=["Status"])
def read_root():
    """A simple endpoint to check if the server is running."""
    return {"message": "PDF Q&A Backend is running"}

@app.post("/upload", tags=["PDF Processing"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF, process it, and create a search index.
    Returns a unique session_id for subsequent queries.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are accepted.")

    # We save the file temporarily to be read by PyMuPDF
    temp_file_path = f"temp_{uuid.uuid4()}.pdf"
    try:
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # 1. Process the PDF to get structured text
        structured_content = extract_structured_text(temp_file_path)
        if not structured_content:
            raise HTTPException(status_code=400, detail="Could not extract any text from the PDF.")

        # 2. Create the FAISS search index
        faiss_index, paragraphs = create_index(structured_content)
        if not faiss_index:
             raise HTTPException(status_code=500, detail="Failed to create search index. The PDF might not contain enough paragraph text.")

        # 3. Create a unique session ID and store the processed data
        session_id = str(uuid.uuid4())
        session_data[session_id] = {
            "index": faiss_index,
            "paragraphs": paragraphs
        }

        return {"session_id": session_id, "filename": file.filename, "message": "File processed successfully. Ready to ask questions."}

    except Exception as e:
        # This will catch any errors during processing
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Clean up by deleting the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/ask", tags=["Q&A"])
def ask(request: AskRequest):
    """
    Endpoint to ask a question based on a previously uploaded PDF.
    Requires a valid session_id.
    """
    session_id = request.session_id
    
    if session_id not in session_data:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a document first.")
    
    # Retrieve the relevant index and paragraphs for this session
    data = session_data[session_id]
    index = data["index"]
    paragraphs = data["paragraphs"]
    
    # 1. Get the context-based answer from the QA engine
    context = answer_question(request.question, index, paragraphs)
    
    # 2. Apply the selected persona
    final_answer = apply_persona(context, request.persona)
    
    return {"answer": final_answer}