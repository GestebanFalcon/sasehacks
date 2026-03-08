import os
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI
from .pipeline import call_pipeline
from .prompting import initial_prompt
from pandas import DataFrame

load_dotenv()

df_raw = DataFrame([
    {
        "account_id": "u1",
        "time": "2026-03-01",
        "rating": 5,
        "review_text": "Battery life is amazing and the screen is super bright."
    },
    {
        "account_id": "u2",
        "time": "2026-03-02",
        "rating": 2,
        "review_text": "Overheats quickly. Not worth the price."
    },
    {
        "account_id": "u3",
        "time": "2026-03-01",
        "rating": 3,
        "review_text": "Very hot phone. Within 5 minutes it was already very hot."
    },
    {
        "account_id": "u4",
        "time": "2026-03-02",
        "rating": 1,
        "review_text": "This phone was very expensive"
    },
    {
        "account_id": "u5",
        "time": "2026-03-01",
        "rating": 5,
        "review_text": "Good"
    },
    {
        "account_id": "u6",
        "time": "2026-03-02",
        "rating": 5,
        "review_text": "I was able to go a long time without needing to charge! The batetry is great. Love this screen!"
    },
])


app = FastAPI()

# ─── Route 1: Simple test route ───────────────────────────────────────────────
@app.get("/hello")
def hello():
    return {"message": "Hello from FastAPI! The server is running."}


# ─── Route 2: Gemini prompt via LangChain ─────────────────────────────────────
@app.get("/ask-deepseek")
def ask_gemini():
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-2.5-flash",
    #     google_api_key=os.getenv("GOOGLE_API_KEY")
    # )

    # prompt = "In exactly 3 bullet points, explain why Python is great for backend development."

    topic_df, topic_summaries = call_pipeline(df_raw)
    content = initial_prompt(topic_summaries)
    
    return {"success": True, "response": content}
