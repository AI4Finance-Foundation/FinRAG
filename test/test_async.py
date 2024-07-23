# main.py
from fastapi import FastAPI
import asyncio
import uvicorn
app = FastAPI()

async def print_hello_world():
    # 模拟异步 I/O
    # await asyncio.sleep(1)
    
    print("Hello, World!")

@app.get("/async-endpoint")
async def root():
    # 模拟异步 I/O，这里可以是任何 I/O 操作，例如读写数据库、文件等
    asyncio.create_task(print_hello_world())
    return {"message": "Task started"}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001)