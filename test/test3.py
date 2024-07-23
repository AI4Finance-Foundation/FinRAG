"""
Author: wangjia
Date: 2024-05-21 01:29:51
LastEditors: wangjia
LastEditTime: 2024-05-21 10:53:28
Description: file content
"""

from app.core.bce.embedding_client import EmbeddingClient
from app.core.preprocessor.file_processor import FileProcesser

if __name__ == "__main__":
    file_path = "example/test3.txt"
    l1_kb = "test1"
    l2_kb = "test2"
    embedding_model = "/data/gpu/base_models/bge-large-zh-v1.5"
    lf = FileProcesser(l1_kb, l2_kb, file_path)
    embedding_client = EmbeddingClient(embedding_model)

    docs = lf.split_file_to_docs()
    docs_content = [doc.page_content for doc in docs]
    embeddings = embedding_client.get_embedding(docs_content)
    print(embeddings[0])
    print(embeddings.shape)
