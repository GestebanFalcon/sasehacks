""""
Take in review summary data and prompt the appropriate LLM for a response.

"""

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek
from pandas import DataFrame
import pandas as pd
from .clustering import top_keyphrases_for_cluster

load_dotenv()

#pass into gemini lmao jk deepseek

prompt = ChatPromptTemplate.from_template("""
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
""")

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0
)

chain = prompt | llm

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
            "avg_rating": float(group["rating"].mean()),
            "keywords": keywords,
            "representative_reviews": representative_reviews,
        }
        topic_summaries.append(summary)

    topic_df = pd.DataFrame(topic_summaries).sort_values(
        "review_count", ascending=False
    ).reset_index(drop=True)

    return (topic_df, topic_summaries)

def initial_prompt(topic_summaries: list): 
    response = chain.invoke({
        "themes": topic_summaries
    })
    return response.content

def re_prompt():
    #yo
    return

