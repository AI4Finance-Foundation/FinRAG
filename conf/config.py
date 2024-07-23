'''
Author: wangjia
Date: 2024-05-26 23:28:10
LastEditors: wangjia
LastEditTime: 2024-05-30 22:29:58
Description: file content
'''

import os

COLLECTION_NAME = "FIN_RAG" # 向量数据库的名称
SENTENCE_SIZE = 500 # 分割的文本长度
DEVICE = "cuda" # 使用cpu还是gpu
EMBEDDING_MODEL = "/data/WoLLM/bce-embedding-base_v1" # embedding 模型的本地路径
RERANK_MODEL = "/data/WoLLM/bce-reranker-base_v1" # rerank 模型的本地路径
MILVUS_URI = "http://localhost:19530" # milvus的uri
NOTIFY_URL = "http://39.96.174.204/api/medical-assistant/knowledge/file/vector/complete" # 向量更新完成后,向后端发送消息的url
CACHE_DIR = ".cache" # 本地缓存路径. 将oss的文件下载这个缓存文件夹里
STORAGE_TYPE="local" # oss # 使用loca还是osss[新增功能]
STORAGE_DIR="/data/storage/" # 本地文件 [新增功能]
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)
    
# 对话内容总结标题的prompt
DIALOGUE_SUMMARY = """为以下对话内容总结一个标题
{context}

请限制在20个字以内
你的回复:"""

# RAG的核心prompt
RAG_PROMPT = """参考信息：
{context}
---
我的问题或指令：
{question}
---
请根据上述参考信息回答我的问题或回复我的指令。
- 我的问题或指令是什么语种，你就用什么语种回复.
- 前面的参考信息可能有用，也可能没用, 请自行判别。
- 如果前面的参考信息与问题有关，你需要从我给出的参考信息中选出与我的问题最相关的那些，来为你的回答提供依据。
- 如果前面的参考信息与问题无关，请回答：根据参考信息,无法得到问题的答案.
- 不要随机编造答案

你的回复："""

if __name__ == "__main__":
    print(RAG_PROMPT.format(context="Hello", question="world"))
