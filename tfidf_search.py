
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
import pandas as pd

class TFIDFSearcher:
    def __init__(self, df: pd.DataFrame, text_columns=None):
        self.df = df.copy()
        if text_columns is None:
            text_columns = ['Form Name','Compliance Title','Description','Keywords','Short Answer']
        self.text_cols = text_columns
        self.docs = (self.df[self.text_cols].fillna('').agg(' '.join, axis=1)).astype(str).tolist()
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.tfidf = self.vectorizer.fit_transform(self.docs)

    def search(self, query: str, top_k=3):
        if not query or len(query.strip())==0:
            return []
        q = query
        qv = self.vectorizer.transform([q])
        cosine_similarities = linear_kernel(qv, self.tfidf).flatten()
        top_idx = np.argsort(cosine_similarities)[::-1][:top_k]
        results = []
        for idx in top_idx:
            if cosine_similarities[idx] > 0:
                results.append(self.df.iloc[idx])
        return results
