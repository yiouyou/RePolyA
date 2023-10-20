import sys, os
import urllib3
urllib3.disable_warnings()
import gradio as gr
# from functools import partial

from repolya.chat import chat_predict_openai
from repolya.rag.vdb_faiss import (
    get_faiss_OpenAI,
    get_faiss_HuggingFace,
)
from repolya.rag.qa_chain import (
    qa_vdb_multi_query,
    qa_docs_ensemble_query,
    qa_docs_parent_query,
)
from repolya.rag.doc_loader import get_docs_from_pdf
from repolya.rag.doc_splitter import split_docs_recursive

from repolya._log import logger_rag
from repolya._const import LOG_ROOT
_log_ans = LOG_ROOT / '_ans.txt'
_log_ref = LOG_ROOT / '_ref.txt'

import time
import concurrent.futures as cf
import threading
from pathlib import Path
_pwd = Path(__file__).absolute()
_path = _pwd.parent


_pdf = str(_path / 'tests' / 'frank' / 'frank_doc.pdf')
_docs = get_docs_from_pdf(_pdf)
_splited_docs = split_docs_recursive(_docs, 1000, 50)
_splited_docs_list = []
for doc in _splited_docs:
    _splited_docs_list.append(doc.page_content)


def chg_btn_color_if_input(_topic):
    if _topic:
        return gr.Button(variant="primary")
    else:
        return gr.Button(variant="secondary")


def qa_faiss_openai(_query):
    start_time = time.time()
    _vdb_name = str(_path / 'tests' / 'frank' / 'frank_doc_openai')
    _vdb = get_faiss_OpenAI(_vdb_name)
    _ans, _step, _token_cost = qa_vdb_multi_query(_query, _vdb, 'stuff')
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"Time: {execution_time:.1f} seconds"
    logger_rag.info(f"{_time}")
    return [_ans, _step, _token_cost, _time]


def qa_faiss_huggingface(_query):
    start_time = time.time()
    _vdb_name = str(_path / 'tests' / 'frank' / 'frank_doc_huggingface')
    _vdb = get_faiss_HuggingFace(_vdb_name)
    _ans, _step, _token_cost = qa_vdb_multi_query(_query, _vdb, 'stuff')
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"Time: {execution_time:.1f} seconds"
    logger_rag.info(f"{_time}")
    return [_ans, _step, _token_cost, _time]


def qa_ensemble(_query):
    start_time = time.time()
    _ans, _step, _token_cost = qa_docs_ensemble_query(_query, _splited_docs_list, 'stuff')
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"Time: {execution_time:.1f} seconds"
    logger_rag.info(f"{_time}")
    return [_ans, _step, _token_cost, _time]


# def frank_doc_helper(_query, _radio):
#     _ans, _ref = "", ""
#     if _radio == "Bundle (udkast)":
#         with cf.ProcessPoolExecutor() as executor:
#             f1 = executor.submit(qa_faiss_openai, _query)
#             f2 = executor.submit(qa_faiss_huggingface, _query)
#             f3 = executor.submit(qa_ensemble, _query)
#             _op = f1.result()
#             _hf = f2.result()
#             _en = f3.result()
#             _ans = f"{_op[0]}\n\n{_hf[0]}\n\n{_en[0]}"
#             _ref = f"{_op[2]}\n{_hf[2]}\n{_en[2]}"
#             _ref += f"\n\n{_op[3]}\n{_hf[3]}\n{_en[3]}"
#     else:
#         _ans = f"ERROR: not supported agent or retriever: {_radio}"
#     return [_ans, _ref]


def write_log_ans(_txt):
    with open(_log_ans, 'w', encoding='utf-8') as wf:
        wf.write(_txt)

def write_log_ref(_txt):
    with open(_log_ref, 'w', encoding='utf-8') as wf:
        wf.write(_txt)

write_log_ans('')
write_log_ref('')

def read_logs():
    with open(_log_ans, "r") as f:
        _ans = f.read()
    with open(_log_ref, "r") as f:
        _ref = f.read()
    return [_ans, _ref]

def frank_doc_helper(_query, _radio):
    _ans, _ref = "", ""
    write_log_ans('')
    write_log_ref('')
    results = {}
    if _radio == "Bundle (udkast)":
        with cf.ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(qa_faiss_openai, _query): "openai",
                executor.submit(qa_faiss_huggingface, _query): "huggingface",
                executor.submit(qa_ensemble, _query): "ensemble"
            }
            for future in cf.as_completed(futures):
                name = futures[future]
                data = future.result()
                results[name] = data
                # Update the Textbox components
                _ans += f"{data[0]}\n\n"
                _ref += f"{data[2]}\n{data[3]}\n\n"
                write_log_ans(_ans)
                write_log_ref(_ref)
    else:
        _ans = f"ERROR: not supported agent or retriever: {_radio}"
        _ref = "..."
        write_log_ans(_ans)
        write_log_ref(_ref)
    return


##### UI
_description = """
# for Frank
"""
chat_ask = gr.Textbox(label="", placeholder="...", lines=5, max_lines=5, interactive=True, visible=True, scale=9)

with gr.Blocks(title=_description) as demo:
    dh_history = gr.State([])
    dh_user_question = gr.State("")
    gr.Markdown(_description)

    with gr.Tab(label = "Ask"):
        fr_query = gr.Textbox(label="Ask", placeholder="...", lines=10, max_lines=10, interactive=True, visible=True)
        fr_radio = gr.Radio(
            ["Bundle (udkast)"],
            label="",
            info="",
            type="value",
            value="Bundle (udkast)"
        )
        fr_start_btn = gr.Button("Start", variant="secondary", visible=True)
        fr_ans = gr.Textbox(label="Ans", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        fr_steps = gr.Textbox(label="Ref", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        fr_query.change(
            chg_btn_color_if_input,
            [fr_query],
            [fr_start_btn]
        )
        fr_start_btn.click(
            read_logs,
            [],
            [fr_ans, fr_steps],
            every=1
        )
        fr_start_btn.click(
            frank_doc_helper,
            [fr_query, fr_radio],
            []
        )
    
    with gr.Tab(label = "Chat4"):
        gr.ChatInterface(
            fn=chat_predict_openai,
            textbox=chat_ask,
            submit_btn="Submit",
            stop_btn="Stop",
            retry_btn="🔄 Retry",
            undo_btn="↩️ Undo",
            clear_btn="🗑️ Clear",
        )




# from fastapi import FastAPI, Response
# import json
# app = FastAPI()

# @app.get("/health")
# def index():
#     return {"message": "active"}

# app = gr.mount_gradio_app(app, demo.queue(), path="/")
## uvicorn ui_cn_pa:app --reload


if __name__ == "__main__":

    import sys
    if len(sys.argv) > 1:
        _port = int(sys.argv[1])
    else:
        _port = 7799

    while True:
        try:
            demo.queue(concurrency_count=1).launch(
                server_name="0.0.0.0",
                server_port=_port,
                share=False,
                favicon_path="./asset/favicon_wa.png",
                ssl_verify=False,
            )
        except Exception as e:
            logger_rag.error(f"{e}")
            continue

    # import uvicorn
    # uvicorn.run(
    #     app,
    #     host="0.0.0.0",
    #     port=7788,
    #     ssl_keyfile="./localhost+2-key.pem",
    #     ssl_certfile="./localhost+2.pem",
    #     reload=True,
    #     debug=True
    # )

