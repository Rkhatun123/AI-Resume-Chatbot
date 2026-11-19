# AI Resume Chatbot 🤖

An AI-powered chatbot that answers questions based on my resume. It uses **Groq LLM**, **FastAPI**, and **React.js** to provide intelligent responses about skills, education, projects, and certifications.

## 🚀 Live Demo

- **Frontend:** https://frontend-seven-phi-32.vercel.app
- **Backend API:** https://ai-resume-chatbot-1fl7.onrender.com
- **API Documentation:** https://ai-resume-chatbot-1fl7.onrender.com/docs

## ✨ Features

- Ask questions about resume information using natural language.
- AI-powered responses using Groq LLM.
- Extracts resume information from PDF.
- Identifies skills, education, projects, and certifications.
- FastAPI backend for handling chat requests.
- React-based interactive chat interface.

## 🛠️ Tech Stack

**Frontend**
- React.js
- Vite
- CSS

**Backend**
- Python
- FastAPI
- Groq API
- Pydantic
- PyPDF

**Deployment**
- Vercel (Frontend)
- Render (Backend)

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Rkhatun123/AI-Resume-Chatbot.git
cd AI-Resume-Chatbot
```

### 2. Backend Setup

```bash
cd backend
pip install fastapi uvicorn groq pydantic python-dotenv pypdf
```

Create a `.env` file in the project root and add:

```env
GROQ_API_KEY=your_groq_api_key
```

Run the backend:

```bash
uvicorn resume_chatbot:app --reload --port 8001
```

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

## 🔐 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key used to access the Groq LLM |

**Note:** The personal resume PDF and API key are not included in this public repository.

## 👩‍💻 Author

**Rani Khatoon**

- GitHub: [Rkhatun123](https://github.com/Rkhatun123)

---

⭐ If you find this project interesting, feel free to explore the repository!
