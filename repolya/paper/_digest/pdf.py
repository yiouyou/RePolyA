from repolya._const import PAPER_DIGEST
from repolya._log import logger_paper
from repolya.paper._digest.vdb_generate import (
    pdf_to_faiss_OpenAI,
    pdf_to_faiss_ST
)
from repolya.paper._digest.vdb_query import (
    qa_faiss_OpenAI_multi_query,
    qa_faiss_ST_multi_query
)

import fitz
from PIL import Image
import os
import io


img_min_width = 120
img_min_height = 120

def get_out_dir(_fp):
    _f = os.path.basename(_fp)
    logger_paper.info(f"{_f}")
    _fn, _ext = os.path.splitext(_f)
    _out_dir = PAPER_DIGEST / _fn
    if not os.path.exists(_out_dir):
        os.makedirs(_out_dir)
    return _out_dir, _fn

##### imgs
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
        # Print the number of images find on this page
        if img_list:
            logger_paper.info(f"[+] Find a total of {len(img_list)} images in page {page_index}")
        else:
            logger_paper.info(f"[!] No images find on page {page_index}")
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
            if image.width >= img_min_width and image.height >= img_min_height:
                out_img = os.path.join(_out_dir, img_name)
                image.save(
                    open(out_img, "wb"),
                    format=img_ext
                )
                _out.append(out_img)
            else:
                logger_paper.info(f"[-] Skipping image {img_index} on page {page_index} due to its small size.")
    return _out


##### text
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
    logger_paper.info(f"[+] {_out_txt}")
    return _out


##### generate faiss
def pdf_to_faiss(_fp):
    _out_dir, _fn = get_out_dir(_fp)
    ### openai
    _db_name_openai = str(_out_dir / 'faiss_openai')
    if not os.path.exists(_db_name_openai):
        pdf_to_faiss_OpenAI(_fp, _db_name_openai)
    else:
        logger_paper.info(f"Find {'/'.join(_db_name_openai.split('/')[-2:])}")
    ### sentence-transformers
    _db_name_st = str(_out_dir / 'faiss_st')
    if not os.path.exists(_db_name_st):
        pdf_to_faiss_ST(_fp, _db_name_st)
    else:
        logger_paper.info(f"Find {'/'.join(_db_name_st.split('/')[-2:])}")


##### multi query faiss
def multi_query_pdf(_fp, _query):
    _out_dir, _fn = get_out_dir(_fp)
    ### openai
    _db_name_openai = str(_out_dir / 'faiss_openai')
    if os.path.exists(_db_name_openai):
        qa_faiss_OpenAI_multi_query(_query, _db_name_openai)
    else:
        logger_paper.info(f"no faiss_openai yet")
    ### sentence-transformers
    _db_name_st = str(_out_dir / 'faiss_st')
    if os.path.exists(_db_name_st):
        qa_faiss_ST_multi_query(_query, _db_name_st)
    else:
        logger_paper.info(f"no faiss_st yet")


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

