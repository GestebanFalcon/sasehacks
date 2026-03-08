"""
Takes in cleaned review data and converts the reviews into their semantic embeddings
"""
from transformers import AutoTokenizer
from transformers import AutoModel
from pandas import DataFrame, Series
import numpy as np
import torch

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")
model = AutoModel.from_pretrained("BAAI/bge-small-en-v1.5")

def generate_embeddings(df: DataFrame):
    df_work = df.copy()
    all_embeddings = []

    batch_size = 32
    with torch.no_grad():
        for i in range (0, len(df_work["review_text"]), batch_size):
            batch = df_work["review_text"][i:i + batch_size].tolist()

            encoded_reviews = tokenizer(batch, padding=True, truncation=True, return_tensors='pt')
            model_output = model(**encoded_reviews)

            # Perform pooling. In this case, cls pooling.   <<--- my best friend is so smart isnt xe <3

            sentence_embeddings = model_output.last_hidden_state[:, 0]
            sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)

            all_embeddings.append(sentence_embeddings.cpu().numpy())

    embeddings = np.vstack(all_embeddings).astype(np.float32)
    df_work["embedding"] = list(embeddings)
    return df_work