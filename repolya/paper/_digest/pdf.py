from repolya._const import PAPER_DIGEST
from repolya._log import logger_paper
from repolya.paper._digest.vdb_generate import (
    pdf_to_faiss_OpenAI,
    pdf_to_faiss_ST,
    get_docs_from_pdf,
    split_docs_recursive,
    split_text_recursive,
)
from repolya.paper._digest.vdb_query import (
    qa_faiss_OpenAI_multi_query,
    qa_faiss_ST_multi_query,
    pretty_print_docs,
)
from repolya.paper._digest.split_sections import clean_and_split

from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import PyMuPDFLoader
from langchain import hub
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import (
    ReduceDocumentsChain,
    MapReduceDocumentsChain,
)
from langchain.chains.llm import LLMChain
from langchain.chains.mapreduce import MapReduceChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.callbacks import get_openai_callback

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
    _fp = os.path.join(_out_dir, _out_txt)
    _text = "========== page ==========\n".join(_out)
    # logger_paper.info(_text)
    with open(_fp, 'w') as wf:
        wf.write(_text)
    logger_paper.info(f"[+] {_out_txt}")
    return _out, _fp


##### generate faiss
def pdf_to_faiss(_fp):
    _out_dir, _fn = get_out_dir(_fp)
    ### openai
    _db_name_openai = str(_out_dir / 'faiss_openai')
    if not os.path.exists(_db_name_openai):
        pdf_to_faiss_OpenAI(_fp, _db_name_openai)
    else:
        logger_paper.info(f"Find '{'/'.join(_db_name_openai.split('/')[-2:])}'")
    # ### sentence-transformers
    # _db_name_st = str(_out_dir / 'faiss_st')
    # if not os.path.exists(_db_name_st):
    #     pdf_to_faiss_ST(_fp, _db_name_st)
    # else:
    #     logger_paper.info(f"Find '{'/'.join(_db_name_st.split('/')[-2:])}'")


##### multi query faiss
def multi_query_pdf(_fp, _query, _chain_type, _if_lotr):
    _ans, _steps = "", ""
    _out_dir, _fn = get_out_dir(_fp)
    if _if_lotr:
        ### sentence-transformers
        _db_name_st = str(_out_dir / 'faiss_st')
        if os.path.exists(_db_name_st):
            _ans, _steps = qa_faiss_ST_multi_query(_query, _db_name_st, _chain_type)
        else:
            logger_paper.info(f"no faiss_st yet")
    else:
        ### openai
        _db_name_openai = str(_out_dir / 'faiss_openai')
        if os.path.exists(_db_name_openai):
            _ans, _steps = qa_faiss_OpenAI_multi_query(_query, _db_name_openai, _chain_type)
        else:
            logger_paper.info(f"no faiss_openai yet")
    return [_ans, _steps]


##### summarize pdf
def summarize_pdf(_fp, _chain_type):
    _ans, _steps = "", ""
    _docs = get_docs_from_pdf(_fp)
    _num_pages = len(_docs)
    _split_docs = split_docs_recursive(_docs)
    if _chain_type == 'stuff':
        if _num_pages > 20:
            _ans = f"文章太长，多达{_num_pages}页，无法使用'快速'模式，请使用'精准'模式。"
        else:
            llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0)
            chain = load_summarize_chain(llm, chain_type="stuff")
            with get_openai_callback() as cb:
                _ans = chain.run(_docs)
                _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
                _steps = f"{_token_cost}\n\n" + f"{'=' * 60} docs\n" + pretty_print_docs(_docs)
                logger_paper.info(f"[stuff] {_ans}")
                logger_paper.info(f"[stuff] {_token_cost}")
                logger_paper.debug(f"[stuff] {_steps}")
    elif _chain_type == 'map_reduce':
        llm = ChatOpenAI(model_name=os.getenv('OPENAI_LLM_MODEL'), temperature=0)
        map_prompt = hub.pull("rlm/map-prompt")
        map_chain = LLMChain(llm=llm, prompt=map_prompt)
        reduce_prompt = hub.pull("rlm/reduce-prompt")
        reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain,
            document_variable_name="doc_summaries"
        )
        reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain=combine_documents_chain,
            collapse_documents_chain=combine_documents_chain,
            token_max=4000,
        )
        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            reduce_documents_chain=reduce_documents_chain,
            document_variable_name="docs",
            return_intermediate_steps=False,
        )
        with get_openai_callback() as cb:
            _ans = map_reduce_chain.run(_split_docs)
            _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
            _steps = f"{_token_cost}\n\n" + f"{'=' * 60} split docs\n" + pretty_print_docs(_split_docs)
            logger_paper.info(f"[map_reduce] {_ans}")
            logger_paper.info(f"[map_reduce] {_token_cost}")
            logger_paper.debug(f"[map_reduce] {_steps}")
    elif _chain_type == 'refine':
        llm = ChatOpenAI(model_name=os.getenv('OPENAI_LLM_MODEL'), temperature=0)
        chain = load_summarize_chain(llm, chain_type="refine")
        with get_openai_callback() as cb:
            _ans = chain.run(_split_docs)
            _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
            _steps = f"{_token_cost}\n\n" + f"{'=' * 60} split docs\n" + pretty_print_docs(_split_docs)
            logger_paper.info(f"[refine] {_ans}")
            logger_paper.info(f"[refine] {_token_cost}")
            logger_paper.debug(f"[refine] {_steps}")
    return [_ans, _steps]


##### summarize pdf_text
def get_pdf_text_for_digest(_fp):
    _out_dir, _fn = get_out_dir(_fp)
    _out_txt = f"{_fn}.txt"
    _fp = os.path.join(_out_dir, _out_txt)
    if not os.path.exists(_fp):
        get_text_from_pdf(_fp)
    with open(_fp, 'r') as rf:
        _fp_text = rf.read()
    _sections = clean_and_split(_fp_text)
    _sec = []
    ### del References
    for i in _sections:
        if i.lower() != "references":
            if i == "_PRE":
                _sec.append(f"{_sections[i]}")
            else:
                _sec.append(f"{i}\n{_sections[i]}")
    _pdf_text = "\n".join(_sec)
    return _pdf_text


def summarize_pdf_text(_fp, _chain_type):
    _ans, _steps = "", ""
    _pdf_text = get_pdf_text_for_digest(_fp)
    _num_text = len(_pdf_text)
    _split_docs = split_text_recursive(_pdf_text, _fp)
    if _chain_type == 'stuff':
        if _num_text > 12000:
            _ans = f"文章太长，多达{_num_text}字符，无法使用'快速'模式，请使用'精准'模式。"
        else:
            llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0)
            chain = load_summarize_chain(llm, chain_type="stuff")
            with get_openai_callback() as cb:
                _ans = chain.run(_split_docs)
                _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
                _steps = f"{_token_cost}\n\n"
                # _steps += f"{'=' * 60} docs\n" + pretty_print_docs(_split_docs)
                logger_paper.info(f"[stuff] {_ans}")
                logger_paper.info(f"[stuff] {_token_cost}")
                logger_paper.debug(f"[stuff] {_steps}")
    elif _chain_type == 'map_reduce':
        llm = ChatOpenAI(model_name=os.getenv('OPENAI_LLM_MODEL'), temperature=0)
        map_prompt = hub.pull("rlm/map-prompt")
        map_chain = LLMChain(llm=llm, prompt=map_prompt)
        reduce_prompt = hub.pull("rlm/reduce-prompt")
        reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain,
            document_variable_name="doc_summaries"
        )
        reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain=combine_documents_chain,
            collapse_documents_chain=combine_documents_chain,
            token_max=4000,
        )
        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            reduce_documents_chain=reduce_documents_chain,
            document_variable_name="docs",
            return_intermediate_steps=False,
        )
        with get_openai_callback() as cb:
            _ans = map_reduce_chain.run(_split_docs)
            _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
            _steps = f"{_token_cost}\n\n"
            # _steps += f"{'=' * 60} split docs\n" + pretty_print_docs(_split_docs)
            logger_paper.info(f"[map_reduce] {_ans}")
            logger_paper.info(f"[map_reduce] {_token_cost}")
            logger_paper.debug(f"[map_reduce] {_steps}")
    elif _chain_type == 'refine':
        llm = ChatOpenAI(model_name=os.getenv('OPENAI_LLM_MODEL'), temperature=0)
        chain = load_summarize_chain(llm, chain_type="refine")
        with get_openai_callback() as cb:
            _ans = chain.run(_split_docs)
            _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
            _steps = f"{_token_cost}\n\n"
            # _steps += f"{'=' * 60} split docs\n" + pretty_print_docs(_split_docs)
            logger_paper.info(f"[refine] {_ans}")
            logger_paper.info(f"[refine] {_token_cost}")
            logger_paper.debug(f"[refine] {_steps}")
    return [_ans, _steps]


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

