"""
Author: Lucas
Date: 2024-05-22 11:21:41
LastEditors: Lucas
LastEditTime: 2024-05-22 11:24:10
Description: file content
"""

import time
from typing import Any, Dict
import requests
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException,BackgroundTasks
from pydantic import BaseModel
import asyncio
from app.core.chat.open_chat import OpenChat
from app.core.vectorstore.customer_milvus_client import CustomerMilvusClient
from app.models.status import ErrorMsg, SuccessMsg
from conf import config
from utils import logger
import json

cmc = CustomerMilvusClient()
open_chat = OpenChat()


class Item(BaseModel):
    syncId: Any
    sysCategory: Any


class Query(BaseModel):
    chatId: Any
    ownerId: Any
    chatName: Any
    initInputs: Dict
    initOpening: Any
    chatMessages: Any


class Notify(BaseModel):
    syncId: Any
    status: Any



def notify_another(notify_msg: Notify):
    logger.info("通知Embedding完成")
    data = {"syncId": notify_msg.syncId, "status": notify_msg.status}
    response = requests.post(config.NOTIFY_URL, 
                            headers={'content-type':'application/json'},
                            data=json.dumps(data))
    # 打印响应的状态码
    print('Status Code:', response.status_code)
    if response.status_code==200:
        logger.info("消息同步成功!")
    # print('Content:', response.message)
    return response

app = FastAPI()

@app.post("/chat")
async def chat(query: Query):
    logger.info("进入Chat")
    # logger.info("query:"+str(query.to_dict()))
    chatId = query.chatId
    ownerId = query.ownerId
    chatName = query.chatName
    initInputs = query.initInputs
    initOpening = query.initOpening
    chatMessages = query.chatMessages
    # logger.info(
    #     str(
    #         {"chatName":chatName,
    #          "initInputs":initInputs,
    #          "chatMessages":chatMessages
    #          }
    #     )
    # )
    logger.info("query:\n***********************************"+
                query.model_dump_json()+
                "\n***********************************")
    messages = [{
        "role": x.get("role").lower(),
        "content": x.get("rawContent")
    } for x in chatMessages]

    try:
        chunks = []
        if len(initInputs.get("categoryIds")) == 0:
            # 开放问答
            logger.info("进入开放域知识问答，答案由完全由大模型生成!")
            response = open_chat.chat(messages)

        else:
            logger.info("进入RAG问答,答案由大模型根据知识库生成！")
            response, retrieval_results = cmc.get_rag_result(
                initInputs, messages)
            if len(retrieval_results):
                chunks = [{
                    "index": x[1],
                    "chunk": x[2],
                    "score": x[0]
                } for x in retrieval_results]
                logger.info("chunks"+str(chunks))
        messages.append({"role": "assistant", "content": response})
        messages.append({
            "role": "user",
            "content": "根据上面我们的历史对话，为我推荐三个接下来我可能要问的问题。每个问题以？结尾"
        })
        suggestedQuestions = open_chat.chat(messages)
        try:
            suggestedQuestions = suggestedQuestions.split('？')
            suggestedQuestions=[x.strip() for x in suggestedQuestions[:3]]
        except:
            suggestedQuestions = [suggestedQuestions]
            
        if chatName == "知识问答助手":
            try:
                new_messages = [
                {
                    "role":"system",
                    "content":"你是一位得力的助手"
                },
                {
                    "role":"user",
                    "content":config.DIALOGUE_SUMMARY.format(context=str(messages[:-1]))
                }
                ]
                chatName = open_chat.chat(new_messages)
                    
                logger.info("大模型总结的chatName:"+str(chatName))
            except:
                chatName = chatName

        return {
            "code": "000000",
            "data": {
                "event": "MESSAGE",
                "result": {
                    "chatId": chatId,
                    "chatName": chatName,
                    "answer": response,
                    "suggestedQuestions": suggestedQuestions,
                    "chunks": chunks,
                },
            },
            "message": "调⽤成功",
            "success": True,
            "time": time.time(),
        }
    except:
        logger.error("RAG问答出错，请检查！")
        return ErrorMsg.to_dict()


async def async_update(item:Item):
    try:
        logger.info("开始更新向量")
        logger.info("syncId:" + str(item.syncId))
        start_time = time.time()
        detail = cmc.parse_request(item)
        cmc.embedding_to_vdb(detail)
        notify_msg = Notify(syncId=item.syncId, status=1)
        end_time = time.time()
        logger.info("Cost time:" + str(end_time - start_time))
        response = notify_another(notify_msg)
        # print(response.message)
        # return SuccessMsg.to_dict()
    except Exception as e:
        # 如果在处理请求时发生错误，返回HTTP 400错误
        # raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}.")
        logger.error("更新向量发生错误!")
        # return ErrorMsg.to_dict()
@app.post("/update_vector")
async def update_vector(item: Item):
    asyncio.create_task(async_update(item))
    return SuccessMsg.to_dict()
    