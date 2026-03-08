import os
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

app = FastAPI()

# ─── Route 1: Simple test route ───────────────────────────────────────────────
@app.get("/hello")
def hello():
    return {"message": "Hello from FastAPI! The server is running."}


# ─── Route 2: Gemini prompt via LangChain ─────────────────────────────────────
@app.get("/ask-gemini")
def ask_gemini():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    prompt = "In exactly 3 bullet points, explain why Python is great for backend development."

    response = llm.invoke(prompt)
    return {"prompt": prompt, "response": response.content}
