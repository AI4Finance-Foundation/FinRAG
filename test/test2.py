'''
Author: wangjia
Date: 2024-05-19 22:42:44
LastEditors: wangjia
LastEditTime: 2024-05-19 22:42:47
Description: file content
'''
from pymilvus import connections, utility

# 创建连接
connections.connect("default", host='localhost', port='19530')

# 检查连接是否正常
try:
    status = utility.get_connection_addr(alias="default")
    print("Connected to Milvus server:", status)
except Exception as e:
    print("Something went wrong:", e)
