"""
Author: wangjia
Date: 2024-05-20 03:31:26
LastEditors: wangjia
LastEditTime: 2024-05-21 11:19:43
Description: file content
"""

import numpy as np
from BCEmbedding import EmbeddingModel

from conf.config import DEVICE


class EmbeddingClient:

    def __init__(self, model_name_or_path) -> None:
        self.model = EmbeddingModel(
            model_name_or_path=model_name_or_path, 
            device=DEVICE,
            trust_remote_code=True,
        )

    def get_embedding(self, sentences):
        embeddings = self.model.encode(sentences)
        return embeddings


if __name__ == "__main__":

    # 读取txt文档，句子列表
    f = open("test.txt", "r", encoding="utf-8")
    doc = f.read().splitlines()
    embedding_client = EmbeddingClient("/data/WoLLM/bce-embedding-base_v1")
    embedding = embedding_client.get_embedding(doc)
    print(embedding.shape)
