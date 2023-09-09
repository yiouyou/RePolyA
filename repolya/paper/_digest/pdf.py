from repolya._const import PAPER_DIGEST
from repolya._log import logger_paper

import fitz
from PIL import Image
import os
import io
import re

from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings


min_width = 120
min_height = 120

def get_out_dir(_fp):
    _f = os.path.basename(_fp)
    logger_paper.info(f"{_f}")
    _fn, _ext = os.path.splitext(_f)
    _out_dir = PAPER_DIGEST / _fn
    if not os.path.exists(_out_dir):
        os.makedirs(_out_dir)
    return _out_dir, _fn


def get_imgs_from_pdf(_fp):
    _pdf = fitz.open(_fp)
    _out_dir, _fn = get_out_dir(_fp)
    _out = []
    # Iterate over PDF pages
    for page_index in range(len(_pdf)):
        # Get the page itself
        page = _pdf[page_index]
        # Get image list
        img_list = page.get_images(full=True)
        # Print the number of images found on this page
        if img_list:
            logger_paper.info(f"[+] Found a total of {len(img_list)} images in page {page_index}")
        else:
            logger_paper.info(f"[!] No images found on page {page_index}")
        # Iterate over the images on the page
        for img_index, img in enumerate(img_list, start=1):
            # Get the XREF of the image
            xref = img[0]
            # Extract the image bytes
            base_img = _pdf.extract_image(xref)
            img_bytes = base_img["image"]
            # Get the image extension
            img_ext = base_img["ext"]
            #Generate image file name
            img_name = f"{_fn}_pg{page_index}_img{img_index}.{img_ext}"
            # Load it to PIL
            image = Image.open(io.BytesIO(img_bytes))
            # Check if the image meets the minimum dimensions and save it
            if image.width >= min_width and image.height >= min_height:
                out_img = os.path.join(_out_dir, img_name)
                image.save(
                    open(out_img, "wb"),
                    format=img_ext
                )
                _out.append(out_img)
            else:
                logger_paper.info(f"[-] Skipping image {img_index} on page {page_index} due to its small size.")
    return _out


def get_text_from_pdf(_fp):
    _pdf = fitz.open(_fp)
    _out_dir, _fn = get_out_dir(_fp)
    _out = []
    _out_txt = f"{_fn}.txt"
    for page_index in range(len(_pdf)):
        # Get the page itself
        page = _pdf[page_index]
        page_text = page.get_text("text") # flags=fitz.TEXT_INHIBIT_SPACES, sort=True
        _out.append(page_text)
    with open(os.path.join(_out_dir, _out_txt), 'w') as wf:
        wf.write("".join(_out))
    logger_paper.info(f"{_out_txt}")
    return _out


def get_docs_from_pdf(_fp):
    _f = os.path.basename(_fp)
    loader = PyMuPDFLoader(str(_fp))
    docs = loader.load()
    logger_paper.info(f"load {len(docs)} pages")
    return docs


def split_docs_recursive(_docs):
    ##### default list is ["\n\n", "\n", " ", ""]
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size = 4000, #1000,
        chunk_overlap = 200, #200,
        length_function = len,
        is_separator_regex = False,
    )
    splited_docs = text_splitter.split_documents(_docs)
    return splited_docs


def embedding_to_faiss_ST(_docs, _db_name):
    _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L12-v2") # all-mpnet-base-v2/all-MiniLM-L6-v2/all-MiniLM-L12-v2
    _db = FAISS.from_documents(_docs, _embeddings)
    _db.save_local(_db_name)
    logger_paper.info(_db_name)
    logger_paper.info("[faiss save HuggingFaceEmbeddings embedding to disk]")


def embedding_to_faiss_OpenAI(_docs, _db_name):
    _embeddings = OpenAIEmbeddings()
    _db = FAISS.from_documents(_docs, _embeddings)
    _db.save_local(_db_name)
    logger_paper.info("/".join(_db_name.split("/")[-2:]))
    logger_paper.info("[faiss save OpenAI embedding to disk]")


def clean_txt(_txt):
    _1 = re.sub(r"\n+", "\n", _txt)
    _2 = re.sub(r"\t+\n", "\n", _1)
    _3 = re.sub(r" +\n", "\n", _2)
    _clean_txt = re.sub(r"\n+", "\n", _3)
    return _clean_txt


def pdf_to_faiss_vdb(_fp, _db_name):
    docs = get_docs_from_pdf(_fp)
    if len(docs) > 0:
        for doc in docs:
            doc.page_content = clean_txt(doc.page_content)
            # print(doc.metadata)
        logger_paper.info(f"docs: {len(docs)}")
        splited_docs = split_docs_recursive(docs)
        logger_paper.info(f"splited_docs: {len(splited_docs)}")
        embedding_to_faiss_OpenAI(splited_docs, _db_name)
        # embedding_to_faiss_ST(splited_docs, _db_name)
    else:
        logger_paper.info("NO docs")


def pdf_to_faiss(_fp):
    _out_dir, _fn = get_out_dir(_fp)
    _db_name = str(_out_dir / 'faiss')
    if not os.path.exists(_db_name):
        pdf_to_faiss_vdb(_fp, _db_name)
    else:
        logger_paper.info(f"found {_db_name}")


##### 转换后行文顺序有问题
##### pip install aspose-words
# import aspose.words as aw
# def pdf_to_md(_fp):
#     _f = os.path.basename(_fp)
#     logger_paper.info(f"{_f}")
#     _fn, _ext = os.path.splitext(_f)
#     out_dir = PAPER_DIGEST / _fn
#     if not os.path.exists(out_dir):
#         os.makedirs(out_dir)
#     _out_md = f"{_fn}.md"
#     # Load PDF file
#     doc = aw.Document(str(_fp))
#     # Save PDF as markdown
#     doc.save(os.path.join(out_dir, _out_md))
#     logger_paper.info(f"{_out_md}")
#     return _out_md

