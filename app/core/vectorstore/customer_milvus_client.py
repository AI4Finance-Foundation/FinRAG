import os

from pymilvus import (Collection, CollectionSchema, DataType, FieldSchema,
                      MilvusClient, connections, utility)

from app.core.bce.embedding_client import EmbeddingClient
from app.core.bce.rerank_client import RerankClient
from app.core.chat.open_chat import OpenChat
from app.core.preprocessor.file_processor import FileProcesser
from app.oss.download_file import Downloader
from conf.config import (CACHE_DIR, COLLECTION_NAME, EMBEDDING_MODEL,
                         MILVUS_URI, RAG_PROMPT, RERANK_MODEL, STORAGE_DIR,
                         STORAGE_TYPE)

embedding_client = EmbeddingClient(EMBEDDING_MODEL)
rerank_client = RerankClient(RERANK_MODEL)
oss_downloader = Downloader()
file_processer = FileProcesser()
open_chat = OpenChat()
_dim = 768

from utils import logger


class CustomerMilvusClient:

    def __init__(self):
        # self.client = MilvusClient(
        #     uri=config.milvus_uri
        # )
        connections.connect(uri=MILVUS_URI)
        self.collection_name = COLLECTION_NAME
        self.collection = self.init()
        self.collection.load()

    def init(self):
        try:
            if utility.has_collection(self.collection_name):
                collection = Collection(self.collection_name)
                logger.info(f"collection {self.collection_name} exists")
            else:
                schema = CollectionSchema(self.fields)
                logger.info(
                    f"create collection {self.collection_name} {schema}")
                collection = Collection(self.collection_name, schema)
                index_params = {
                    "metric_type": "L2",
                    "index_type": "IVF_FLAT",
                    "params": {
                        "nlist": 2048
                    },
                }
                collection.create_index(field_name="embedding",
                                        index_params=index_params)
                logger.info("初始化成功!")
        except Exception as e:
            logger.error(e)
        return collection

    def embedding_to_vdb(self, file_details, batch_size=1000):
        """
        当文档过长时，会出现无法一次性插入向量数据库的情况，因此需要分批插入
        """
        for file_info in file_details:
            fileName = file_info.get("fileName")
            fileSuffix = file_info.get("fileSuffix")
            storagePath = file_info.get("storagePath")
            local_file = CACHE_DIR + "/" + fileName
            logger.info(f"正在将文件【{fileName}】下载到本地缓存...")
            try:
                oss_downloader.get_file(storagePath, local_file)
            except:
                logger.error("下载失败，请检查网络或检查文件是否存在")
            logger.info("本地文件地址:" + str(local_file))
            docs = file_processer.split_file_to_docs(local_file)
            docs_content = [doc.page_content for doc in docs]
            embeddings = embedding_client.get_embedding(docs_content)
            entities = []
            try:
                for idx, cont, emb in zip(range(len(docs)), docs_content,
                                          embeddings):
                    entity = {
                        "parentId": file_info.get("parentId"),
                        "categoryName": file_info.get("categoryName"),
                        "categoryId": file_info.get("categoryId"),
                        "fileId": str(file_info.get("fileId")),
                        "fileName": fileName,
                        "fileSuffix": fileSuffix,
                        "storagePath": storagePath,
                        "chunkId": idx,
                        "chunkContent": cont,
                        "embedding": emb,
                    }
                    entities.append(entity)
                    if len(entities) == batch_size:
                        self.collection.insert(entities)
                        self.collection.flush()
                        entities = []
                self.collection.insert(entities)
                self.collection.flush()
                logger.info("存入向量数据库成功！")
            except:
                logger.error(str(local_file) + "写入向量数据库失败，请检查！")

    def parse_request(self, data):
        # # 解析JSON字符串
        # data = json.loads(json_str)
        # 初始化一个空列表来存储结果
        file_details = []

        # 遍历JSON数据结构
        for category in data.sysCategory:
            # 首先获取顶级分类中的文件存储信息
            for file_storage in category.get("fileStorages", []):
                file_details.append({
                    "fileName": file_storage["fileName"],
                    "fileSuffix": file_storage["fileSuffix"],
                    "storagePath": file_storage["storagePath"],
                    "categoryName": category["categoryName"],
                    "categoryId": category["categoryId"],
                    "parentId": category["parentId"],
                })

            # 然后获取子分类中的文件存储信息
            for sub_category in category.get("subCategory", []):
                for file_storage in sub_category.get("fileStorages", []):
                    file_details.append({
                        "fileName":
                        file_storage["fileName"],
                        "fileSuffix":
                        file_storage["fileSuffix"],
                        "storagePath":
                        file_storage["storagePath"],
                        "categoryName":
                        sub_category["categoryName"],
                        "categoryId":
                        sub_category["categoryId"],
                        "parentId":
                        sub_category["parentId"],
                    })

            # 打印结果
            for detail in file_details:
                print(detail)
        return file_details

    @property
    def fields(self):
        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                auto_id=True,
                max_length=100,
            ),
            FieldSchema(name="parentId",
                        dtype=DataType.VARCHAR,
                        max_length=256),
            FieldSchema(name="categoryName",
                        dtype=DataType.VARCHAR,
                        max_length=256),
            FieldSchema(name="categoryId",
                        dtype=DataType.VARCHAR,
                        max_length=256),
            FieldSchema(name="fileId", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="fileName",
                        dtype=DataType.VARCHAR,
                        max_length=1024),
            FieldSchema(name="fileSuffix",
                        dtype=DataType.VARCHAR,
                        max_length=256),
            FieldSchema(name="storagePath",
                        dtype=DataType.VARCHAR,
                        max_length=256),
            FieldSchema(name="chunkId", dtype=DataType.INT64),
            FieldSchema(name="chunkContent",
                        dtype=DataType.VARCHAR,
                        max_length=1024),
            FieldSchema(name="embedding",
                        dtype=DataType.FLOAT_VECTOR,
                        dim=_dim),  # 向量字段
        ]
        return fields

    @property
    def output_fields(self):
        return [
            "parentId",
            "categoryName",
            "categoryId",
            "fileId",
            "fileName",
            "fileSuffix",
            "storagePath",
            "chunkId",
            "chunkContent",
            "embedding",
        ]

    def delete_collection(self):
        self.collection.release()
        utility.drop_collection(self.collection_name)
        print("向量数据库重置成功!")

    def get_rag_result(self, initInputs, messages):
        query = messages[-1].get("content")
        logger.info(f"最新的问题是：【{query}】")
        query_emb = embedding_client.get_embedding(query)
        categoryIds = initInputs.get("categoryIds")
        topK = initInputs.get('topK')
        score = initInputs.get('score')
        logger.info("score:" + str(score))
        if len(categoryIds) > 1:
            # rerank
            rag_results = []
            reference_results = []
            for idStr in categoryIds:
                category_ids = idStr.split(',')
                rag_result, retrival_results = self.retrieval_and_generate(
                    query_emb, topK, score, category_ids, messages)

                rag_results.append(rag_result)
                reference_results.extend(retrival_results)

            rereank_results = self.rerank(query, rag_results)
            rag_result = rag_results[rereank_results['rerank_ids'].index(0)]
            retrival_results = reference_results
        else:
            category_ids = categoryIds[0].split(',')
            rag_result, retrival_results = self.retrieval_and_generate(
                query_emb, topK, score, category_ids, messages)
        return rag_result, retrival_results

    def retrieval_and_generate(self, query_emb, topK, score, category_ids,
                               messages):
        expr = "categoryId in {}".format(category_ids)
        logger.info(expr)
        search_params = {
            "metric_type": "L2",
            "offset": 0,
            "ignore_growing": False,
            "params": {
                "nprobe": 10
            }
        }

        results = self.collection.search(
            data=query_emb,
            anns_field="embedding",
            param=search_params,
            limit=topK,
            expr=expr,
            output_fields=['fileName', 'chunkContent'],
            consistency_level="Strong")
        relevant_content = []
        for hits in results:
            for hit in hits:
                print(hit)
                print(f"ID: {hit.id}, score: {hit.score}")
                print(f"chunkContent: {hit.entity.get('chunkContent')})")
                relevant_content.append((hit.score, hit.entity.get("fileName"),
                                         hit.entity.get('chunkContent')))
        logger.info("检索到相关片段的数量是:%d" % len(relevant_content))
        if len(relevant_content) > 0:
            retrival_results = [x for x in relevant_content if x[0] > score]
            retrival_results_text = [x[2] for x in retrival_results]
            logger.info("检索到的片段:" + str(retrival_results_text))
            retrieval_result_str = '\n\n'.join(retrival_results_text)
        else:
            retrival_results = []
            retrieval_result_str = ""

        messages[-1]['content'] = RAG_PROMPT.format(
            context=retrieval_result_str, question=messages[-1]['content'])
        rag_result = open_chat.chat(messages)

        return rag_result, retrival_results

    # def generate(self, messages, retrieval_result):
    #     messages[-1]['content'] = RAG_PROMPT.format(
    #         context=retrieval_result, question=messages[-1]['content'])
    #     ans = open_chat.chat(messages)
    #     return ans

    def rerank(self, query, multi_result):
        logger.info('进入rerank模块')
        rerank_result = rerank_client.rerank(query, multi_result)
        return rerank_result
