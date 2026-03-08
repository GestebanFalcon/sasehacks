import pandas as pd
from pandas import DataFrame
from .cleaning import clean_df
from .embedding import generate_embeddings
from .clustering import cluster_embeddings
from .prompting import generate_summaries



def call_pipeline(df_raw):

    df = clean_df(df_raw)
    df = generate_embeddings(df)
    df = cluster_embeddings(df)

    topic_df, topic_summaries = generate_summaries(df)

    #for now return summary - potential for improvement in future iterations for more advanced acecssing
    return (topic_df, topic_summaries)

