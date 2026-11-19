import json
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel, Field
from pypdf import PdfReader


# Load environment variables
load_dotenv()

# Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

model = "openai/gpt-oss-120b"

# FastAPI application
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resume PDF path
BASE_DIR = Path(__file__).resolve().parent
RESUME_FILE = Path("/etc/secrets/resume.txt")
# RESUME_FILE = BASE_DIR / "resume.pdf"


# -----------------------------
# Resume Data Models
# -----------------------------

class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skills_used: list[str] = Field(default_factory=list)


class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    total_experience_years: float | None = None

    skills: list[str] = Field(default_factory=list)
    experiences: list[Experience] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


# Generate JSON schema
resume_schema = Resume.model_json_schema()


# -----------------------------
# Chat Request Model
# -----------------------------

class ChatRequest(BaseModel):
    question: str


# -----------------------------
# PDF Text Extraction
# -----------------------------

def read_pdf(file_path: Path):

    if not file_path.exists():
        raise FileNotFoundError(
            f"Resume file not found: {file_path}"
        )

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise ValueError(
            "No readable text found in the PDF."
        )

    return text


# -----------------------------
# Resume Parsing using Groq
# -----------------------------

def parse_resume(resume_text: str):

    system_prompt = f"""
You are an expert resume parser.

Extract information from the resume based on its meaning,
not only based on exact section headings.

Different resumes may use different headings.

For example:
- Experience
- Professional Experience
- Work History
- Employment
- Internships

These may all contain relevant experience.

Skills may also appear in the skills section, work experience,
internships or projects.

Return ONLY valid JSON matching this schema:

{json.dumps(resume_schema, indent=2)}

Important rules:

1. Do not invent information.
2. If a value is not available, return null.
3. If a list has no information, return an empty list.
4. Include internships inside experiences.
5. Extract skills mentioned across the entire resume.
6. Do not calculate or assume experience unless clearly supported.
"""

    user_prompt = f"""
Parse the following resume:

{resume_text}
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={
            "type": "json_object"
        }
    )

    raw_output = response.choices[0].message.content

    data = json.loads(raw_output)

    resume = Resume(**data)

    return resume


# -----------------------------
# HR Question Answering (Streaming)
# -----------------------------

def ask_candidate(question: str, resume: Resume):

    system_prompt = f"""
You are an AI assistant representing a job candidate.

Below is everything you know about the candidate.

{resume.model_dump_json(indent=2)}

Rules:

1. Answer only using this information.
2. Never hallucinate.
3. If information is unavailable, say:
   "I don't have enough information to answer that."
4. Be professional.
5. Answer as if HR is interviewing this candidate.
6. Keep answers clear and concise.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ],
        stream=True
    )

    for chunk in response:

        content = chunk.choices[0].delta.content

        if content:
            yield content


# -----------------------------
# Home API
# -----------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to AI Resume Chatbot"
    }


# -----------------------------
# Resume API
# -----------------------------

@app.get("/resume")
def get_resume():

    try:
        resume_text = read_pdf(RESUME_FILE)
        resume = parse_resume(resume_text)

        return resume.model_dump()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# -----------------------------
# Chat API (Streaming)
# -----------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    try:
        # Step 1: Read PDF
        resume_text = read_pdf(RESUME_FILE)

        # Step 2: Parse resume
        resume = parse_resume(resume_text)

        # Step 3: Stream AI answer
        return StreamingResponse(
            ask_candidate(
                request.question,
                resume
            ),
            media_type="text/plain"
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
