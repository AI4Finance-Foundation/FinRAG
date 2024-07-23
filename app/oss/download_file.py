"""
Author: Lucas
Date: 2024-05-21 10:25:18
LastEditors: Lucas
LastEditTime: 2024-05-22 12:55:53
Description: file content
"""

import os
import shutil

import dotenv
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider

from conf.config import STORAGE_DIR, STORAGE_TYPE

dotenv.load_dotenv()
endpoint = os.getenv("END_POINT")
bucket_name = os.getenv("BUCKET_NAME")

class Downloader:
    def __init__(self) -> None:
        auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)

    def get_file(self, remote, local):
        if STORAGE_TYPE=='local':
            return self.get_local_file(remote, local)
        else:
            return self.get_oss_file(remote, local)
        
    def get_local_file(self,remote,local):
        shutil.copy(os.path.join(STORAGE_DIR,remote),local)
        return 
    def get_oss_file(self,remote,local):
        # 首先判断本地是否有缓存, 如果有, 跳过; 没有,下载
        if local in os.listdir(".cache"):
            return
        if local is None:
            local = ".cache/" + remote.split("/")[-1]
        self.bucket.get_object_to_file(remote, local)
        return