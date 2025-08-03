import os
import re
import docx
import email
import requests
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv
import PyPDF2
from email import policy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from openai import OpenAI

# Load environment variables
load_dotenv()
APIKEY = os.getenv("api_key")

# Clean text function
def clean_text(text: str) -> str:
    return text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")

# Unified Document Assistant
class UnifiedDocAssistant:
    def __init__(self):
        self.document_text = ""

    def load_file(self, file_obj, filename: str):
        ext = filename.lower().split('.')[-1]
        try:
            if ext.find("pdf") != -1:
                print("Loading PDF file...")
                return self._load_pdf(file_obj)
            elif ext == "docx":
                return self._load_docx(file_obj)
            elif ext == "eml":
                return self._load_eml(file_obj)
            else:
                return "Unsupported file format"
        except Exception as e:
            return f"Error reading document: {e}"

    def _load_pdf(self, file_obj):
        print("Extracting text from PDF...")
        if not file_obj:
            print("No file object provided for PDF extraction.")
        reader = PyPDF2.PdfReader(file_obj)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        self.document_text = text.strip()
        if not self.document_text:
            print("No text extracted from PDF.")
        else:
            print(f"Extracted {len(self.document_text)} characters from PDF.")
        return "PDF extracted"

    def _load_docx(self, file_obj):
        doc = docx.Document(file_obj)
        text = "\n".join(p.text for p in doc.paragraphs)
        self.document_text = clean_text(text.strip())
        return "DOCX extracted"

    def _load_eml(self, file_obj):
        msg = email.message_from_binary_file(file_obj, policy=policy.default)
        text = msg.get_body(preferencelist=('plain')).get_content()
        self.document_text = clean_text(text.strip())
        return "EML extracted"

    def ask_question(self, question: str):
        if not self.document_text:
            return self.document_text

        client = OpenAI(api_key=APIKEY, base_url="https://openrouter.ai/api/v1")
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant. If the question is not relevant to the document:\n\n{self.document_text}\n\nJust respond: 'Not relevant to the document'."},
                {"role": "user", "content": question}
            ],
            temperature=0.6,
            top_p=0.95,
            max_tokens=2048,
            stream=False
        )
        if self.document_text:
            return response.choices[0].message.content.strip().replace("*", "") + "\n\nDocument context:\n" + self.document_text[:500]  # Limit context to first 500 chars
        return self.document_text

# FastAPI app setup
app = FastAPI()
assistant = UnifiedDocAssistant()

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class HackRxRequest(BaseModel):
    documents: str  # Document URL
    questions: List[str]

# Document processing logic
def process_document_from_url(document_url: str):
    response = requests.get(document_url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Unable to fetch document from URL")

    filename = document_url.split("/")[-1]
    result = assistant.load_file(BytesIO(response.content), filename)

    if "Error" in result:
        raise HTTPException(status_code=500, detail=result)
    return result

# Main API route
@app.post("/api/v1/hackrx/run")
async def hackrx_run(data: HackRxRequest):
    try:
        res = process_document_from_url(data.documents)
        print(f"Document processed: {res}")
        answers = []
        for q in data.questions:
            ans = assistant.ask_question(q)
            answers.append({"question": q, "answer": ans})
        return {"document": data.documents, "answers": answers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
