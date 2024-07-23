'''
Author: wangjia
Date: 2024-05-19 00:04:14
LastEditors: wangjia
LastEditTime: 2024-05-26 14:38:05
Description: file content
'''
from loguru import logger
from datetime import datetime
import time
import sys


class Logger:

    @classmethod
    def get_logger(self):
        folder_ = "logs/"
        prefix_ = "mylog-"
        rotation_ = "10 MB"
        retention_ = "30 days"
        encoding_ = "utf-8"
        backtrace_ = True
        diagnose_ = True

        # 格式里面添加了process和thread记录，方便查看多进程和线程程序
        format_ = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
            "|<level>{level: <7}</level>"
            "|<cyan>{name}</cyan>:<cyan>{function}</cyan>:<yellow>{line}</yellow>"
            "|<level>{message}</level>")

        # 这里面采用了层次式的日志记录方式，就是低级日志文件会记录比他高的所有级别日志，这样可以做到低等级日志最丰富，高级别日志更少更关键
        # debug
        logger.add(
            folder_ + prefix_ + "debug.log",
            level="DEBUG",
            backtrace=backtrace_,
            diagnose=diagnose_,
            format=format_,
            colorize=False,
            rotation=rotation_,
            retention=retention_,
            encoding=encoding_,
            filter=lambda record: record["level"].no >= logger.level("DEBUG").
            no,
        )

        # info
        logger.add(
            folder_ + prefix_ + "info.log",
            level="INFO",
            backtrace=backtrace_,
            diagnose=diagnose_,
            format=format_,
            colorize=False,
            rotation=rotation_,
            retention=retention_,
            encoding=encoding_,
            filter=lambda record: record["level"].no >= logger.level("INFO").
            no,
        )

        # warning
        logger.add(
            folder_ + prefix_ + "warning.log",
            level="WARNING",
            backtrace=backtrace_,
            diagnose=diagnose_,
            format=format_,
            colorize=False,
            rotation=rotation_,
            retention=retention_,
            encoding=encoding_,
            filter=lambda record: record["level"].no >= logger.level("WARNING")
            .no,
        )

        # error
        logger.add(
            folder_ + prefix_ + "error.log",
            level="ERROR",
            backtrace=backtrace_,
            diagnose=diagnose_,
            format=format_,
            colorize=False,
            rotation=rotation_,
            retention=retention_,
            encoding=encoding_,
            filter=lambda record: record["level"].no >= logger.level("ERROR").
            no,
        )

        # critical
        logger.add(
            folder_ + prefix_ + "critical.log",
            level="CRITICAL",
            backtrace=backtrace_,
            diagnose=diagnose_,
            format=format_,
            colorize=False,
            rotation=rotation_,
            retention=retention_,
            encoding=encoding_,
            filter=lambda record: record["level"].no >= logger.level("CRITICAL"
                                                                     ).no,
        )

        logger.add(
            sys.stderr,
            level="CRITICAL",
            backtrace=backtrace_,
            diagnose=diagnose_,
            format=format_,
            colorize=True,
            filter=lambda record: record["level"].no >= logger.level("CRITICAL"
                                                                     ).no,
        )

        return logger


# 自定义日志输出
logger = Logger.get_logger()

# 获取当前时间,并格式化日期时间
current_time = datetime.now()
current_date = current_time.strftime("%Y-%m-%d")
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")


# 计算时间函数
def timeit(func):

    def wrapper(*args, **kw):
        start_time = time.time()
        result = func(*args, **kw)
        cost_time = time.time() - start_time
        print("==" * 25)
        print("Current Function [%s] run time is %s s" %
              (func.__name__, cost_time))
        print("==" * 25)
        return result

    return wrapper
