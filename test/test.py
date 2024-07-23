"""
Author: wangjia
Date: 2024-05-19 22:18:54
LastEditors: wangjia
LastEditTime: 2024-05-20 03:33:35
Description: file content
"""

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections

from app.core.bce.embedding_client import EmbeddingClient

connections.connect("default", host="localhost", port="19530")
embedding_client = EmbeddingClient("/data/WoLLM/bce-embedding-base_v1")

# 读取txt文档，句子列表
f = open("test.txt", "r", encoding="utf-8")
doc = f.read().splitlines()

embeddings = embedding_client.get_embedding(doc)

fields = [
    FieldSchema(
        name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=True, max_length=100
    ),
    FieldSchema(name="kb_name", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="chunk_id", dtype=DataType.INT64),
    FieldSchema(name="chunk_content", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),  # 向量字段
]

schema = CollectionSchema(fields=fields)
# 创建 collection
# print("client is connected:", client.is_connected())
collection = Collection("test_collection3", schema=schema)
# 添加索引
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128},
}
# 字段 filmVector 创建索引
collection.create_index("embedding", index_params)

entities = [["test_kb"] * len(doc), doc, range(len(doc)), doc, embeddings]
collection.insert(entities)
# 记得在插入数据后调用 flush 来确保数据被写入到磁盘
collection.flush()
print(collection)
collection.load()
