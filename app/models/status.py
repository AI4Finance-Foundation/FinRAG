'''
Author: wangjia
Date: 2024-05-19 00:10:00
LastEditors: wangjia
LastEditTime: 2024-05-24 00:02:48
Description: file content
'''
# class Status:
#     status_code = ""
#     status_msg = ""
import time


class ErrorMsg:
    code = "xxxxxx"
    data = None
    message= "调⽤失败"
    success= False
    @classmethod
    def to_dict(cls):
        return {
            'code': cls.code,
            'data': cls.data,
            'message': cls.message,
            'success': cls.success,
            'time': time.time(),  # 获取当前时间
        }
class SuccessMsg():
    code = "000000"
    data = None
    message= "调⽤成功"
    success= True
    @classmethod
    def to_dict(cls):
        return {
            'code': cls.code,
            'data': cls.data,
            'message': cls.message,
            'success': cls.success,
            'time': time.time(),  # 获取当前时间
        }

if __name__ == '__main__':
    sm = SuccessMsg()
    sm.to_dict()