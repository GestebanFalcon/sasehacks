""""
Take in review summary data and prompt the appropriate LLM for a response.

"""

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_deepseek import ChatDeepSeek
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pandas import DataFrame, Series
import pandas as pd
from .clustering import top_keyphrases_for_cluster
from sklearn.metrics.pairwise import cosine_similarity
load_dotenv()


# ----- 0. Setup -----
prompt_text = """
You are an expert e-commerce product analyst.

Your task is to analyze a set of customer review summaries and produce a
clear purchasing recommendation. Speak directly to the consumer. Be easy to understand, as if you are talking to your grandmother.

Review Themes:
{themes}

Instructions:
1. Identify the most common positive features.
2. Identify the most common complaints.
3. Identify any recurring product issues.
4. Determine if customers generally recommend buying the product.

Output Format:

Product Strengths:
- ...

Product Weaknesses:
- ...

Major Themes:
- ...

Overall Recommendation:
Buy / Avoid / Mixed
"""
base_prompt = ChatPromptTemplate.from_template(prompt_text)
prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder("history", optional=True),
])

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0
)


# ----- 1. Util Functions -----

def generate_summaries(df: DataFrame):
    topic_summaries = []

    for topic_id, group in df.groupby("topic_id"):
        group = group.sort_values("topic_center_sim", ascending=False)

        representative_reviews = group["review_text"].head(3).tolist()
        keywords = top_keyphrases_for_cluster(group["review_text"].tolist(), n=5)

        summary = {
            "topic_id": int(topic_id),
            "review_count": int(len(group)),
            "share_of_reviews": float(len(group) / len(df)),
            "keywords": keywords,
            "representative_reviews": representative_reviews,
        }
        topic_summaries.append(summary)

    topic_df = pd.DataFrame(topic_summaries).sort_values(
        "review_count", ascending=False
    ).reset_index(drop=True)

    return (topic_df, topic_summaries)


# ----- 2. Tools -----

@tool
def search_reviews(query: str, session_id: int) -> str:
    """
        Search through the reviews to find specific reviews matching the query
        This is useful when looking for specific information that may have been touched upon by the reviews or specific sentiments contained in the reviews.
        Results may or may not contain what you are looking for.
    """
    return "I didnt find anything gng"

llm_tools = llm.bind_tools([search_reviews])
chain = prompt | llm_tools
basic_chain = prompt | llm


# ----- 3. Prompting -----

def initial_prompt(topic_summaries: list): 
    """Returns history with initial prompt. This could probably throw. I need to add error handling later."""

    #format_messages() also works here. this is a bit more readable
    initial_message = SystemMessage(content=base_prompt.format(themes=topic_summaries))
    history = [initial_message]

    response = basic_chain.invoke({
        "history": history,
        "tool_choice": "none"
    })

    history.append(response)
    return history

def re_prompt(history):
    """Modifies history in place. Returns nothing"""
    #yo
    oldHistory = [res.content for res in history]
    print(oldHistory)
    response = chain.invoke({
        "history": history
    })

    print(response.content)
    
    if not response.tool_calls:
        history.append(response)
        newHistory = [res.content for res in history]
        # print(newHistory)
        return

    tool_results = []
    for tool in response.tool_calls:
        tool_result = ""
        if tool["name"] == "search_reviews":
            tool_result = "no relevant reviews found :("

        tool_results.append({"name": tool["name"], "result": tool_result})

    history.append(SystemMessage(content=f"Tool call results: {tool_results}"))

    #no looping reprompts for now     
    response = chain.invoke({
        "history": history
    })        

    history.append(response)
    newHistory = [res.content for res in history]

    # print(newHistory)
    return

