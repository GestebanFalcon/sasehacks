"""
Take in review embeddings and provide clustered groups - utilizes K-Means
Also provides keyphrase generation util
"""

from keybert import KeyBERT
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pandas import DataFrame  

kw_model = KeyBERT()

def cosine_to_center(vec, center):
        return cosine_similarity(vec.reshape(1, -1), center.reshape(1, -1))[0, 0]

def cluster_embeddings(df: DataFrame):
    df_work = df.copy()
    X = np.vstack(df_work["embedding"].values)

    n_clusters = min(6, max(2, len(df) // 20)) #why did gpt make it max
    kmeans = KMeans(n_clusters=n_clusters, random_state = 42, n_init=10) #dont know what random state or n init do lol
    df_work["topic_id"] = kmeans.fit_predict(X)

    # Distance to centroid -> useful for representative reviews
    centroids = kmeans.cluster_centers_

    df_work["topic_center_sim"] = [
        cosine_to_center(X[i], centroids[df_work.iloc[i]["topic_id"]])
        for i in range(len(df_work))
    ]

    return df_work 

def top_keyphrases_for_cluster(texts, n=5):
  if len(texts) == 0:
    return []
  docs = ' '.join(texts)
  keyphrases = kw_model.extract_keywords(docs, keyphrase_ngram_range=(3, 5), top_n=n, stop_words="english")
  return keyphrases