# GenAI Document Assistant

## Project Description
A full-stack GenAI-powered document assistant that processes user-uploaded PDF or TXT documents and intelligently handles two core tasks:
- Deep document comprehension and question answering with explicit, snippet-based justification.
- Generation and evaluation of logic-based questions for user self-assessment, with grounded feedback.

## Functional Flow
### 1. Document Upload
- User uploads a PDF or TXT file.
- The backend parses and chunks the document, stores embeddings in a vector store (FAISS).
- An LLM generates a concise summary (≤150 words), displayed immediately.

### 2. Interaction Modes
#### Ask Anything
- User asks free-form questions about the document.
- System retrieves relevant chunks, answers using RAG, and cites the exact snippet location (e.g., "Paragraph 3, Page 2").

#### Challenge Me
- System generates 3 logic/reasoning-based questions from the document.
- User answers each; system grades (correct/partial/incorrect) and provides feedback with evidence from the document.

## Setup Instructions
### Python Environment
- Python 3.9+
- Recommended: Create a virtual environment

### Install Requirements
```
pip install -r requirements.txt
```

### API Keys
- If using OpenAI or other LLM APIs, set your API key as an environment variable:
  - `OPENAI_API_KEY=your-key-here`

### Running the App
1. **Backend (FastAPI):**
   ```
   uvicorn backend.app:app --reload
   ```
2. **Frontend (Streamlit):**
   ```
   streamlit run frontend/app.py
   ```

## Reasoning Architecture
### Question Generation
- Uses LLM to generate logic-based questions grounded in document content.
- Ensures questions require inference, not just fact recall.

### Answer Grounding
- All answers are justified with explicit document snippets (with location references).
- No hallucination: answers must be supported by the source document.

### Evaluation (Challenge Me)
- User answers are compared to reference answers using semantic similarity and keyword matching.
- Grading: correct / partially correct / incorrect, with feedback and evidence snippet.

---

**Bonus:**
- Answer highlighting: UI shows exact evidence in bold or highlight.
- All code modularized for easy extension (see backend/utils for parsing/chunking logic). 