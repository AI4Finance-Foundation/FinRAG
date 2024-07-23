
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, UnstructuredFileLoader, UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader)

from app.core.splitter import ChineseTextSplitter, zh_title_enhance
from conf import config
from utils import logger

text_splitter = RecursiveCharacterTextSplitter(
    separators=[
        "\n",
        ".",
        "。",
        "!",
        "！",
        "?",
        "？",
        "；",
        ";",
        "……",
        "…",
        "、",
        "，",
        ",",
        " ",
    ],
    chunk_size=300,
    # length_function=num_tokens,
)


class FileProcesser:

    def __init__(self):
        logger.info(f"Success init file processor")

    def split_file_to_docs(self,
                           file_path,
                           sentence_size=config.SENTENCE_SIZE):
        logger.info("开始解析文件,文件越大,解析所需时间越长,大文件请耐心等待...")
        file_type = file_path.split('.')[-1].lower()

        if file_type == "txt":
            loader = TextLoader(file_path, autodetect_encoding=True)
            texts_splitter = ChineseTextSplitter(pdf=False,
                                                 sentence_size=sentence_size)
            docs = loader.load_and_split(texts_splitter)
        elif file_type == "pdf":
            loader = UnstructuredPDFLoader(file_path)
            texts_splitter = ChineseTextSplitter(pdf=True,
                                                 sentence_size=sentence_size)
            docs = loader.load_and_split(texts_splitter)
        elif file_type == "docx":
            loader = UnstructuredWordDocumentLoader(file_path, mode="elements")
            texts_splitter = ChineseTextSplitter(pdf=False,
                                                 sentence_size=sentence_size)
            docs = loader.load_and_split(texts_splitter)
        else:
            raise TypeError("文件类型不支持，目前仅支持：[txt,pdf,docx]")
        # docs = zh_title_enhance(docs)
        # 重构docs，如果doc的文本长度大于800tokens，则利用text_splitter将其拆分成多个doc
        # text_splitter: RecursiveCharacterTextSplitter
        logger.info(f"before 2nd split doc lens: {len(docs)}")
        docs = text_splitter.split_documents(docs)
        logger.info(f"after 2nd split doc lens: {len(docs)}")
        self.docs = docs
        return docs
