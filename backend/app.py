from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
from .utils.document_parser import parse_document
from .utils.chunker import chunk_document
from .summarizer import generate_summary
import tempfile
from .qa_engine import answer_question
from .question_generator import generate_questions
from .evaluator import grade_answers
import openai

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory doc store (for demo)
doc_store = {}

class UploadResponse(BaseModel):
    doc_id: str
    summary: str

class AskRequest(BaseModel):
    doc_id: str
    question: str

class AskResponse(BaseModel):
    answer: str
    evidence: str
    location: str

class ChallengeQuestion(BaseModel):
    question: str
    reference_answer: str
    evidence: str
    location: str

class ChallengeResponse(BaseModel):
    questions: List[ChallengeQuestion]

class GradeRequest(BaseModel):
    doc_id: str
    user_answers: List[str]

class GradeFeedback(BaseModel):
    grade: str
    feedback: str
    evidence: str
    location: str

class GradeResponse(BaseModel):
    results: List[GradeFeedback]

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    # Parse document
    parsed = parse_document(tmp_path)
    # Chunk document
    chunks = chunk_document(parsed)
    # Concatenate all text for summary
    full_text = " ".join([item['text'] for item in parsed])
    summary = generate_summary(full_text)
    doc_id = str(uuid.uuid4())
    doc_store[doc_id] = {
        "filename": file.filename,
        "summary": summary,
        "parsed": parsed,
        "chunks": chunks
    }
    os.remove(tmp_path)
    return {"doc_id": doc_id, "summary": summary}

@app.post("/ask", response_model=AskResponse)
async def ask_anything(request: AskRequest):
    doc = doc_store.get(request.doc_id)
    if not doc:
        return JSONResponse(status_code=404, content={"error": "Document not found"})
    answer, evidence, location = answer_question(request.question, doc['chunks'])
    return {"answer": answer, "evidence": evidence, "location": location}

@app.get("/challenge", response_model=ChallengeResponse)
async def get_challenge_questions(doc_id: str):
    doc = doc_store.get(doc_id)
    if not doc:
        return JSONResponse(status_code=404, content={"error": "Document not found"})
    questions = generate_questions(doc['chunks'])
    # Store questions for grading
    doc['challenge_questions'] = questions
    # Convert to ChallengeQuestion models
    challenge_questions = [
        ChallengeQuestion(
            question=q['question'],
            reference_answer=q['reference_answer'],
            evidence=q['evidence'],
            location=q['location']
        ) for q in questions
    ]
    return {"questions": challenge_questions}

@app.post("/challenge/grade", response_model=GradeResponse)
async def grade_challenge(request: GradeRequest):
    doc = doc_store.get(request.doc_id)
    if not doc or 'challenge_questions' not in doc:
        return JSONResponse(status_code=404, content={"error": "Document or challenge questions not found"})
    questions = doc['challenge_questions']
    reference_answers = [q['reference_answer'] for q in questions]
    evidences = [q['evidence'] for q in questions]
    locations = [q['location'] for q in questions]
    results = grade_answers(request.user_answers, reference_answers, evidences, locations)
    grade_feedback = [
        GradeFeedback(
            grade=r['grade'],
            feedback=r['feedback'],
            evidence=r['evidence'],
            location=r['location']
        ) for r in results
    ]
    return {"results": grade_feedback}

def generate_summary(text):
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Summarize: {text}"}],
        )
        return response.choices[0].message.content
    except openai.RateLimitError:
        return "OpenAI quota exceeded. (This is a mock summary for development.)"
