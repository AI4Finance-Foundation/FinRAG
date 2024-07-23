FROM python:3.10-slim
# 镜像元信息
LABEL MAINTAINER=wangjia
# 环境设置
ENV LANG=C.UTF-8
ENV TZ=Asia/Shanghai
WORKDIR /FinRAG
COPY . /FinRAG
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
EXPOSE 8000
CMD ["/bin/bash", "/bin/start.sh"]
