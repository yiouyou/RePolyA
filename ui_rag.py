import sys, re
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
    qa_summerize,
)
from repolya.rag.doc_loader import get_docs_from_pdf
from repolya.rag.doc_splitter import split_pdf_docs_recursive

from repolya.autogen.workflow import create_rag_task_list, search_faiss_openai
from repolya.autogen.util import cost_usage
from repolya.rag.qa_chain import qa_with_context, summerize_text
# from autogen import ChatCompletion

from repolya._log import logger_rag
from repolya._const import LOG_ROOT, WORKSPACE_RAG
_log_ans1 = LOG_ROOT / '_ans1.txt'
_log_ref1 = LOG_ROOT / '_ref1.txt'
_log_ans2 = LOG_ROOT / '_ans2.txt'
_log_ref2 = LOG_ROOT / '_ref2.txt'

import time
import concurrent.futures as cf
import threading


##### log
def read_logs():
    with open(_log_ans1, "r") as f:
        _ans1 = f.read()
    with open(_log_ref1, "r") as f:
        _ref1 = f.read()
    with open(_log_ans2, "r") as f:
        _ans2 = f.read()
    with open(_log_ref2, "r") as f:
        _ref2 = f.read()
    return [_ans1, _ref1, _ans2, _ref2]

def write_log_ans(_log_ans, _txt, _status=None):
    with open(_log_ans, 'w', encoding='utf-8') as wf:
        if _status == "continue":
            _txt += "\n\n计算中，请稍候..."
        elif _status == "done":
            _txt += "\n\n完成！"
        wf.write(_txt)

def write_log_ref(_log_ref, _txt):
    with open(_log_ref, 'w', encoding='utf-8') as wf:
        wf.write(_txt)

def clean_logs():
    write_log_ans(_log_ans1,'')
    write_log_ref(_log_ref1,'')
    write_log_ans(_log_ans2,'')
    write_log_ref(_log_ref2,'')

def clean_all():
    clean_logs()
    return [gr.Textbox(value=""), gr.Button(variant="secondary")]

clean_logs()


##### btn, textbox
def chg_btn_color_if_input(_topic):
    if _topic:
        return gr.Button(variant="primary")
    else:
        return gr.Button(variant="secondary")

def chg_textbox_visible(_radio):
    if _radio == '快速':
        return {
            fr_ans1: gr.Textbox(visible=True),
            fr_log1: gr.Textbox(visible=True),
            fr_ans2: gr.Textbox(visible=False),
            fr_log2: gr.Textbox(visible=False),
        }
    if _radio == '高级':
        return {
            fr_ans1: gr.Textbox(visible=False),
            fr_log1: gr.Textbox(visible=False),
            fr_ans2: gr.Textbox(visible=True),
            fr_log2: gr.Textbox(visible=True),
        }


##### RAG
def qa_faiss_openai(_query):
    start_time = time.time()
    _vdb_name = str(WORKSPACE_RAG / 'lj_rag_openai')
    _vdb = get_faiss_OpenAI(_vdb_name)
    _ans, _step, _token_cost = qa_vdb_multi_query(_query, _vdb, 'stuff')
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"Time: {execution_time:.1f} seconds"
    logger_rag.info(f"{_time}")
    return [_ans, _step, _token_cost, _time]

def qa_sum(_txt_fp):
    start_time = time.time()
    _ans, _token_cost = qa_summerize(_txt_fp, 'stuff')
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"Time: {execution_time:.1f} seconds"
    logger_rag.info(f"{_time}")
    return [_ans, _token_cost, _time]

def sum_token_cost_from_text(text):
    """Extract and sum tokens, cost, and time from a given text."""
    token_matches = re.findall(r"Tokens: (\d+)", text)
    cost_matches = re.findall(r"Cost: \$([0-9.]+)", text)
    time_matches = re.findall(r"Time: ([0-9.]+) seconds", text)
    total_tokens = sum(int(token) for token in token_matches)
    total_cost = sum(float(cost) for cost in cost_matches)
    ### 除了最后一步，前面几步都是并行的，所以只计算最后两个时间
    total_time = sum(float(time) for time in time_matches[-2:])
    _out = f"Tokens: {total_tokens}\nCost: ${format(total_cost, '.3f')}\nTime: {total_time:.1f} seconds"
    return _out

def frank_doc_helper_fast(_query, _radio):
    _ans, _ref = "", ""
    write_log_ans(_log_ans1,'')
    write_log_ref(_log_ref1,'')
    results = {}
    if _radio == "快速":
        with cf.ProcessPoolExecutor() as executor:
            write_log_ans(_log_ans1, '', 'continue')
            futures = {
                executor.submit(qa_faiss_openai, _query): "openai",
            }
            for future in cf.as_completed(futures):
                name = futures[future]
                data = future.result()
                results[name] = data
                # Update the Textbox components
                _ans += f"{data[0]}\n\n"
                _ref += f"{data[2]}\n{data[3]}\n\n"
                write_log_ans(_log_ans1, _ans, 'continue')
                write_log_ref(_log_ref1, _ref)
            _sum, _c, _t = qa_sum(_log_ans1)
            _ans = f"{_sum}\n\n" + "-"*20 + " references\n" + _ans
            _ref += f"{_c}\n{_t}\n\n"
            _sum_ref = sum_token_cost_from_text(_ref)
            _ref = f"{_sum_ref}\n\n" + "-"*20 + " references\n" + _ref
            # write_log_ans(_ans, 'done')
            # write_log_ref(_ref)
            write_log_ans(_log_ans1, _sum, 'done')
            write_log_ref(_log_ref1, _sum_ref)
    return

def frank_doc_helper_advanced(_query, _radio):
    _ans, _ref = "", ""
    write_log_ans(_log_ans2,'')
    write_log_ref(_log_ref2,'')
    results = {}
    if _radio == "高级":
        start_time = time.time()
        write_log_ans(_log_ans2, '', 'continue')
        # ChatCompletion.start_logging(reset_counter=True, compact=False)
        ### task list
        _task_list = create_rag_task_list(_query)
        write_log_ans(_log_ans2, f"Generated sub-questions list:\n\n{_task_list}", 'continue')
        end_time = time.time()
        execution_time = end_time - start_time
        _time = f"Time: {execution_time:.1f} seconds"
        write_log_ref(_log_ref2, f"\n\n{_time}")
        # print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")
        ### context
        _context = search_faiss_openai(_task_list)
        write_log_ans(_log_ans2, f"Generated QA context:\n\n{_context}", 'continue')
        end_time = time.time()
        execution_time = end_time - start_time
        _time = f"Time: {execution_time:.1f} seconds"
        write_log_ref(_log_ref2, f"\n\n{_time}")
        ### qa
        _qa, _tc = qa_with_context(_query, _context)
        write_log_ans(_log_ans2, f"Generated final answer:\n\n{_qa}", 'done')
        end_time = time.time()
        execution_time = end_time - start_time
        _time = f"Time: {execution_time:.1f} seconds"
        write_log_ref(_log_ref2, f"\n\n{_time}\n\n{'='*40}\n\n{_context}")
    return


##### UI
_description = """
# 问答-知识库
"""
chat_ask = gr.Textbox(label="", placeholder="...", lines=5, max_lines=5, interactive=True, visible=True, scale=9)

with gr.Blocks(title=_description) as demo:
    dh_history = gr.State([])
    dh_user_question = gr.State("")
    gr.Markdown(_description)

    with gr.Tab(label = "提问"):
        fr_query = gr.Textbox(label="提问", placeholder="...", lines=10, max_lines=10, interactive=True, visible=True)
        fr_radio = gr.Radio(
            ["快速", "高级"],
            label="",
            info="",
            type="value",
            value="快速",
        )
        fr_start_btn = gr.Button("开始", variant="secondary", visible=True)
        fr_clean_btn = gr.Button("清空", variant="secondary", visible=True)
        with gr.Row():
            fr_ans1 = gr.Textbox(label="回答 (快速)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
            fr_ans2 = gr.Textbox(label="回答 (高级)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=False)
        with gr.Row():
            fr_log1 = gr.Textbox(label="日志 (快速)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
            fr_log2 = gr.Textbox(label="日志 (高级)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=False)
        fr_radio.change(
            chg_textbox_visible,
            [fr_radio],
            [fr_ans1, fr_ans2, fr_log1, fr_log2]
        )
        fr_query.change(
            chg_btn_color_if_input,
            [fr_query],
            [fr_start_btn]
        )
        fr_start_btn.click(
            read_logs,
            [],
            [fr_ans1, fr_log1, fr_ans2, fr_log2],
            every=1
        )
        fr_start_btn.click(
            frank_doc_helper_fast,
            [fr_query, fr_radio],
            []
        )
        fr_start_btn.click(
            frank_doc_helper_advanced,
            [fr_query, fr_radio],
            []
        )
        fr_clean_btn.click(
            clean_all,
            [],
            [fr_query, fr_start_btn]
        )
    
    with gr.Tab(label = "聊天"):
        gr.ChatInterface(
            fn=chat_predict_openai,
            textbox=chat_ask,
            submit_btn="提交",
            stop_btn="停止",
            retry_btn="🔄 重试",
            undo_btn="↩️ 撤消",
            clear_btn="🗑️ 清除",
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
        _port = 7788

    while True:
        try:
            demo.queue(concurrency_count=1).launch(
                server_name="0.0.0.0",
                server_port=_port,
                share=False,
                favicon_path="./asset/favicon_paper.png",
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

