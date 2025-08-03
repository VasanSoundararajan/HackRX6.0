import mimetypes
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup
import email
from dotenv import load_dotenv
import email.policy
from openai import OpenAI
import os
import re
import requests
from urllib.parse import urlparse

# utils.py
import mimetypes
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup
import email
from dotenv import load_dotenv
import email.policy
from openai import OpenAI
import os
import re

class UnifiedDocAssistant:
    def __init__(self):
        self.document_text = ""

    def load_file(self, file_obj, filename: str):
        ext = filename.split(".")
        if "pdf" in ext:
            return self._load_pdf(file_obj)
        elif any(x in ext for x in ["docx", "docs", "word", "docm", "document"]):
            return self._load_docx(file_obj)
        elif "eml" in ext:
            return self._load_eml(file_obj)
        elif "txt" in ext:
            return self._load_txt(file_obj)
        else:
            return f"Unsupported file extension: .{ext}"

    def _load_pdf(self, file_obj):
        try:
            reader = PdfReader(file_obj)
            self.document_text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return "PDF loaded successfully."
        except Exception as e:
            return f"Error loading PDF: {str(e)}"

    def _load_docx(self, file_obj):
        try:
            doc = Document(file_obj)
            text = "\n".join(p.text for p in doc.paragraphs)
            self.document_text = text.strip()
            return "DOCX loaded successfully."
        except Exception as e:
            return f"Error loading DOCX: {str(e)}"

    def _load_eml(self, file_obj):
        try:
            msg = email.message_from_binary_file(file_obj, policy=email.policy.default)
            parts = [msg.get_body(preferencelist=('plain', 'html')).get_content()]
            self.document_text = "\n".join(parts)
            return "EML loaded successfully."
        except Exception as e:
            return f"Error loading EML: {str(e)}"

    def _load_txt(self, file_obj):
        try:
            self.document_text = file_obj.read().decode('utf-8')
            return "TXT loaded successfully."
        except Exception as e:
            return f"Error loading TXT: {str(e)}"

    def ask_question(self, question):
        client = OpenAI(
            api_key="API KEY HERE",  # Replace with your actual API key
            base_url="https://integrate.api.nvidia.com/v1"
        )

        if not self.document_text:
            return "No document loaded to provide context."

        response = client.chat.completions.create(
            model="nvidia/llama-3.3-nemotron-super-49b-v1.5",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful assistant. If the user's question is not relevant to this document:\n\n{self.document_text}\n\nSay 'Not relevant to the document' without any explanation. Use this document as context."
                },
                {"role": "user", "content": question}
            ],
            temperature=0.6,
            top_p=0.95,
            max_tokens=2048,
            stream=False
        )

        return self.format_answer(response.choices[0].message.content.strip().replace("*", ""))

    def format_answer(self, raw_answer: str) -> str:
        cleaned = re.sub(r"<think>.*?</think>", "", raw_answer, flags=re.DOTALL).strip()
        return cleaned
# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from io import BytesIO
import requests
import mimetypes
import os

from utils import UnifiedDocAssistant  # Assuming you have this implemented

app = FastAPI()
assistant = UnifiedDocAssistant()

# Allow CORS (optional if using frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HackRxRequest(BaseModel):
    documents: str  # URL to document (PDF, DOCX, EML, TXT)
    questions: List[str]

@app.post("/api/v1/hackrx/run")
async def hackrx_run(data: HackRxRequest):
    try:
        # Step 1: Fetch document from URL
        response = requests.get(data.documents)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download document from provided URL.")

        # Step 2: Determine filename and extension
        filename = data.documents.split("/")[-1].split("?")[0]
        if '.' not in filename:
            raise HTTPException(status_code=400, detail="Cannot determine file extension from URL.")
        
        # Step 3: Load document using assistant
        load_status = assistant.load_file(BytesIO(response.content), filename)
        if not assistant.document_text.strip():
            raise HTTPException(status_code=422, detail="Document was parsed but no text was extracted.")

        # Step 4: Ask questions
        answers = [
            {"question": q, "answer": assistant.ask_question(q)}
            for q in data.questions
        ]

        return JSONResponse(content={
            "document": filename,
            "status": load_status,
            "answers": answers
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


