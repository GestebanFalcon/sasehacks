import os
from typing import TypedDict
from json import JSONDecodeError

import psycopg2
from pandas import DataFrame
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from langchain_core.messages import HumanMessage

from .pipeline import call_pipeline
from .scraping import fetch_reviews
from .cleaning import clean_df
from .embedding import generate_embeddings
from .clustering import cluster_embeddings
from .prompting import generate_summaries, initial_prompt, re_prompt
from db import init_chat, insert_message, delete_session, get_connection

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

origins = [
    "http://localhost:3000"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─── Route 1: Simple test route ───────────────────────────────────────────────
@app.get("/hello")
def hello():
    return {"message": "Hello from FastAPI! The server is running."}

def prompt_llm(url: str): #horribly named rn
    reviews = fetch_reviews(url)
    if reviews is None:
        return {"success": False, "response": "No reviews found. Try a different link"}

    raw_df = DataFrame(reviews)

    df = clean_df(raw_df)
    df = generate_embeddings(df)
    df = cluster_embeddings(df)
    topic_df, topic_summaries = generate_summaries(df)

    res = initial_prompt(topic_summaries)
    #should not fucking throw unless the actual prompt fail
    content = res[1].content
    
    return {"success": True, "response": content, "df": df}


# ─── Route 2: Gemini prompt via LangChain ─────────────────────────────────────
@app.post("/ask-deepseek")
def ask_gemini(url: str):
    print("yo")
    res = prompt_llm(url)
    return {"success": res["success"], "response": res["response"]}


# --- Route 3: Websocket Route (idk if this coutns  as a route but wtv) -----
           
#Note: naming convention changing from df to reviews_df. Contains review data + embedding column

class ChatMessage(TypedDict):
    role: str
    content: str

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    session_id = None
      
    try:
        # ----- Step 1: Init and populate needed variables -----
        reviews_df = DataFrame()
        chat_history = []

        # --- No Cookie: Default handling Initial request - just send url ---
        message = await websocket.receive_json()

        if ("url" not in message):
            await websocket.send_json({
                "error": "Error: Missing Field, fields event or message missing from message"
            })
            await websocket.close(code=1008)
            return

        if ("event" not in message or message["event"] != "init"):
            await websocket.send_json({
                "error": "Error: This is a terrible fucking structure holy shit. But you didn't put event: init here."
            })
        
        url = message["url"]


        # i need to add better error checking. Before i was using the res with internal checking, here ill use external checking ig idk.

        print("test test")

        try:
            reviews = fetch_reviews(url)
            if reviews is None:
                raise Exception("no reviews found")
            
            raw_df = DataFrame(reviews)
                
            df = clean_df(raw_df)
            df = generate_embeddings(df)
            df = cluster_embeddings(df)
            topic_df, topic_summaries = generate_summaries(df)
            print("testing")
            chat_history = initial_prompt(topic_summaries)
            print("do we ever even reach here")

        except Exception as err:
            await websocket.send_json({
                "error": "Error: Internal server error while initializing conversation."
            })
            await websocket.close(code=1011)
            print("bruh something broke")
            return

        reviews_df = df
        
        try:
            session_id = init_chat(reviews_df, chat_history[-1].content)
        except psycopg2.Error as err:
            await websocket.send_json({
                "error": "Error: Internal server error while initializing conversation."
            })
            print(err)
            await websocket.close(code=1011)
            return

        await websocket.send_json({
            "event": "init",
            "success": True,
            "response": chat_history[-1].content
        })
        print("we did it hehe")
        # --- Cookie Detected: Do shit idk unimplemented ---

        # burger code

        # ----- Step 2: User/conversation info fetched - Main Listening Loop -----
        #session_id should be defined past here. Will be handled by cookie later likely./

        while True:
            #New pattern: event, data
            message = await websocket.receive_json()
            print("handling new jawn")
            # --- Parse Input ---
            # Handle bad data format. keep connection alive ig.
            if ("event" not in message or "data" not in message):
                await websocket.send_json({
                    "error": "Error: Missing Field, fields event or message missing from message."
                })
                continue
             
            event: str = message["event"]
            data: str = message["data"]
            #can validate later with isinstance or pydantic. Python version of zod ig.

            # --- Handle Events ---
            if (event == "re_prompt"):
                #if session_id is broken ima crash out yo.
                
                try:

                    with get_connection() as conn:
                        #Add user message
                        insert_message(conn, data, "user", session_id)
                        chat_history.append(HumanMessage(content=data))
                        #Prompt chatbot. Need to add error checking
                        re_prompt(chat_history)

                        #no way its empty right
                        response = chat_history[-1].content

                        #Record chatbot message
                        insert_message(conn, response, "assistant", session_id)   

                        #Send user new state
                        await websocket.send_json({
                            "success": True,
                            "response": response,
                            "event": "new_message"
                        })
                        print("sent jawn!")
                        print(response)
                            
                except psycopg2.Error as err:
                    await websocket.send_json({
                        "error": "Error: Internal Server Error attempting to reprompt LLM."
                    })
                    continue
                except Exception as err:
                    await websocket.send_json({
                        "error": "Error: idk i need better error checking. Error calling LLM probably."
                    })

            #More events idk..
            #...

    except JSONDecodeError as err:
        await websocket.send_json({
            "error": "Error: Invalid JSON, please send valid JSON."
        })
        await websocket.close(code=1003)
        return

    except WebSocketDisconnect:
        with get_connection() as conn:
            # !!!!! 🚨WATCH OUT GNG🚨 !!!!! 🚨CRAB 🦀 ERROR🚨 !!!!!
            delete_session(conn, session_id)
            # i  genly dont know what to do if this fails so ill keep this here3 for later. i dont wanna bloat the db or nothing.
            # maybe when i add timeout that will fully handle it and i can just handle this by catching and doing nothing. idk 

    return