


import base64
import os
from typing import Any, Callable, List, Union

import fitz
import numpy as np
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from paddleocr import PaddleOCR
from tqdm import tqdm
from unstructured.partition.text import partition_text

ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=True, show_log=False)


class UnstructuredPaddlePDFLoader(UnstructuredFileLoader):
    """Loader that uses unstructured to load image files, such as PNGs and JPGs."""

    def __init__(
        self,
        file_path: Union[str, List[str]],
        # ocr_engine: Callable,
        mode: str = "single",
        **unstructured_kwargs: Any,
    ):
        """Initialize with file path."""
        self.ocr_engine = ocr_engine
        super().__init__(file_path=file_path, mode=mode, **unstructured_kwargs)

    def _get_elements(self) -> List:
        def pdf_ocr_txt(filepath, dir_path="tmp"):
            full_dir_path = os.path.join(os.path.dirname(filepath), dir_path)
            if not os.path.exists(full_dir_path):
                os.makedirs(full_dir_path)
            doc = fitz.open(filepath)
            txt_file_path = os.path.join(
                full_dir_path, "{}.txt".format(os.path.split(filepath)[-1])
            )
            img_name = os.path.join(full_dir_path, "tmp.png")
            with open(txt_file_path, "w", encoding="utf-8") as fout:
                for i in tqdm(range(doc.page_count)):
                    page = doc.load_page(i)
                    pix = page.get_pixmap()
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                        (pix.h, pix.w, pix.n)
                    )
                    img_file = base64.b64encode(img).decode("utf-8")
                    height, width, channels = pix.h, pix.w, pix.n

                    binary_data = base64.b64decode(img_file)
                    img_array = np.frombuffer(binary_data, dtype=np.uint8).reshape(
                        (height, width, channels)
                    )
                    # result = self.ocr_engine(img_array)
                    result = self.ocr_engine.ocr(img_array)
                    result = [line for line in result if line]
                    ocr_result = [i[1][0] for line in result for i in line]
                    fout.write("\n".join(ocr_result))
            if os.path.exists(img_name):
                os.remove(img_name)
            return txt_file_path

        txt_file_path = pdf_ocr_txt(self.file_path)
        return partition_text(filename=txt_file_path, **self.unstructured_kwargs)


if __name__ == "__main__":

    ...
    # from paddleocr import PaddleOCR
    # from app.core.text_splitter.chinese_text_splitter import ChineseTextSplitter

    # file_path = "附件4-1：广银理财幸福理财日添利开放式理财计划第2期产品说明书（百信银行B份额）.pdf"
    # ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=True, show_log=False)
    # loader = UnstructuredPaddlePDFLoader(file_path, ocr_engine)
    # texts_splitter = ChineseTextSplitter(pdf=True, sentence_size=250)
    # docs = loader.load_and_split(texts_splitter)
    # print(docs)

