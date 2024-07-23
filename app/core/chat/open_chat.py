'''
Author: xubing
Date: 2024-05-22 23:43:54
LastEditors: xubing
LastEditTime: 2024-05-23 19:44:13
Description: file content
'''
import os

from openai import OpenAI
from utils import logger

class OpenChat:
    def __init__(self) -> None:
        self.client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"), # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope SDK的base_url
    )
    def chat(self,messages):
        logger.info(str(messages))
        completion = self.client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        stream=False
        )
        result = completion.choices[0].message.content
        print(result)
        return result

if __name__=="__main__":
    oc = OpenChat()
    raw_messsages = [
    {
    "chatMessageId": "m00001",
    "role": "system",
    "rawContent": "你是⼀个医疗助⼿"
    },
    {
    "chatMessageId": "m00002",
    "role": "user",
    "rawContent": "我感冒了吃什么药"
    },
    {
    "chatMessageId": "m00003",
    "role": "assistant",
    "rawContent": "你要是999感冒灵"
    },
    {
    "chatMessageId": "m00004",
    "role": "user",
    "rawContent": "我吃了999感觉没什么⽤"
    }
    ]
    messages = [
        {
            "role": x.get('role').lower(),
            "content": x.get("rawContent")
        }
        for x in raw_messsages
    ]
    print(messages)
    oc.chat(messages)

