import os

from openai import OpenAI


class RAGChat:
    def __init__(self) -> None:
        self.client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"), # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope SDK的base_url
    )
    def chat(self,messages):
        query = messages[-1].get("content")
        query_emb = ''

        completion = self.client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        stream=False
        )
        result = completion.choices[0].message.content
        print(result)
        return result