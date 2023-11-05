import sys, re
import urllib3
urllib3.disable_warnings()
import gradio as gr
# from functools import partial
import concurrent.futures as cf
import threading
import time
import shutil
import os
import ast

from repolya.chat import chat_predict_openai
from repolya.rag.vdb_faiss import (
    get_faiss_OpenAI,
    get_faiss_HuggingFace,
    merge_faiss_openai,
)
from repolya.rag.qa_chain import (
    qa_vdb_multi_query,
    qa_docs_ensemble_query,
    qa_docs_parent_query,
    qa_summerize,
    qa_with_context_as_mio,
)
from repolya.rag.doc_loader import (
    get_docs_from_pdf,
    clean_txt,
)
from repolya.rag.doc_splitter import split_pdf_docs_recursive
from repolya.rag.digest_dir import (
    calculate_md5,
    dir_to_faiss_openai,
)
from repolya.autogen.wf_jd import (
    generate_search_query_for_event,
    generate_vdb_for_search_query,
    generate_event_context,
    generate_event_plan,
)
from repolya._log import logger_rag
from repolya._const import LOG_ROOT, WORKSPACE_RAG, WORKSPACE_AUTOGEN
# from autogen import ChatCompletion


_log_ans1 = LOG_ROOT / '_ans1.txt'
_log_ref1 = LOG_ROOT / '_ref1.txt'
_log_ans2 = LOG_ROOT / '_ans2.txt'
_log_ref2 = LOG_ROOT / '_ref2.txt'
_log_ans3 = LOG_ROOT / '_ans3.txt'
_log_ref3 = LOG_ROOT / '_ref3.txt'
_log_ans_ml = LOG_ROOT / '_ans_ml.txt'
_log_ref_ml = LOG_ROOT / '_ref_ml.txt'
_log_ans_yj_context = LOG_ROOT / '_ans_yj_context.txt'
_log_ans_yj_plan = LOG_ROOT / '_ans_yj_plan.txt'
_log_ref_yj = LOG_ROOT / '_ref_yj.txt'

from repolya.toolset.tool_bshr import bshr_vdb
from repolya.autogen.workflow import (
    create_jdml_task_list_zh,
    create_rag_task_list_zh,
    search_faiss_openai,
)

from ui_rag_JQ import JQ_openai_tagging


##### tagging
def read_file(file):
    if file:
        with open(file.name, encoding="utf-8") as f:
            content = f.read()
            return content

def chg_btn_color_if_file(file):
    if file:
        return gr.Button(variant="primary")
    else:
        return gr.Button(variant="secondary")

def llm_JQ(file_name):
    import os
    import re
    _log = ""
    _JQ_str = ""
    _total_cost_str = ""
    # print(f"file_name: {file_name}")
    if os.path.exists(file_name):
        left, right = os.path.splitext(os.path.basename(file_name))
        global output_JQ_file
        output_JQ_file = f"{left}_JQ.txt"
        with open(file_name, encoding='utf-8') as rf:
            _txt = rf.read()
        txt_lines = clean_txt(_txt)
        txt_lines = txt_lines.split('\n')
        [_log, _JQ_str, _total_cost_str, _sentences] = JQ_openai_tagging(txt_lines)
        with open(output_JQ_file, "w", encoding='utf-8') as wf:
            wf.write(_JQ_str)
        # _JQ = ast.literal_eval(_JQ_str)
        # print(type(_JQ), _JQ)
    return _log

def run_llm_JQ(file):
    if file:
        return llm_JQ(file.name)
    else:
        return ["错误: 请先上传一个TXT文件！"]

def show_JQ_file(text):
    # print(f"text: {text}")
    if text:
        if output_JQ_file:
            return gr.File(value=output_JQ_file, visible=True)
    else:
        if output_JQ_file:
            return gr.File(value=output_JQ_file)


##### upload dir
_upload_dir = WORKSPACE_RAG / 'lj_rag_upload'
if not os.path.exists(_upload_dir):
    os.makedirs(_upload_dir)
_db_name = str(WORKSPACE_RAG / 'lj_rag_openai')
_db_name_new = str(WORKSPACE_RAG / 'lj_rag_new_openai')
_clean_txt_dir = str(WORKSPACE_RAG / 'lj_rag_clean_txt')

##### log
def write_log_ans(_log_ans, _txt, _status=None):
    with open(_log_ans, 'w', encoding='utf-8') as wf:
        if _status == "continue":
            _txt += "\n\n计算中，请稍候..."
        # elif _status == "done":
        #     _txt += "\n\n[完成]"
        wf.write(_txt)

def write_log_ref(_log_ref, _txt):
    with open(_log_ref, 'w', encoding='utf-8') as wf:
        wf.write(_txt)

def add_log_ref(_log_ref, _txt):
    with open(_log_ref, 'a', encoding='utf-8') as wf:
        wf.write(f"\n\n{_txt}")

def rag_read_logs():
    with open(_log_ans1, "r") as f:
        _ans1 = f.read()
    with open(_log_ref1, "r") as f:
        _ref1 = f.read()
    with open(_log_ans2, "r") as f:
        _ans2 = f.read()
    with open(_log_ref2, "r") as f:
        _ref2 = f.read()
    with open(_log_ans3, "r") as f:
        _ans3 = f.read()
    with open(_log_ref3, "r") as f:
        _ref3 = f.read()
    return [_ans1, _ref1, _ans2, _ref2, _ans3, _ref3]

def ml_read_logs():
    with open(_log_ans_ml, "r") as f:
        _ans_ml = f.read()
    with open(_log_ref_ml, "r") as f:
        _ref_ml = f.read()
    return [_ans_ml, _ref_ml]

def yj_read_logs():
    with open(_log_ref_yj, "r") as f:
        _ref_yj = f.read()
    with open(_log_ans_yj_context, "r") as f:
        _ans_yj_context = f.read()
    with open(_log_ans_yj_plan, "r") as f:
        _ans_yj_plan = f.read()
    return [_ref_yj, _ans_yj_context, _ans_yj_plan]

def rag_clean_logs():
    write_log_ans(_log_ans1,'')
    write_log_ref(_log_ref1,'')
    write_log_ans(_log_ans2,'')
    write_log_ref(_log_ref2,'')
    write_log_ans(_log_ans3,'')
    write_log_ref(_log_ref3,'')

def ml_clean_logs():
    write_log_ans(_log_ans_ml,'')
    write_log_ref(_log_ref_ml,'')

def yj_clean_logs():
    write_log_ref(_log_ref_yj,'')
    write_log_ans(_log_ans_yj_context,'')
    write_log_ans(_log_ans_yj_plan,'')

rag_clean_logs()
ml_clean_logs()
yj_clean_logs()

def rag_clean_all():
    rag_clean_logs()
    print('rag_clean_logs()')
    return [gr.Textbox(value=""), gr.Button(variant="secondary")]

def ml_clean_all():
    ml_clean_logs()
    print('ml_clean_logs()')
    return [gr.Textbox(value=""), gr.Button(variant="secondary")]

def yj_clean_all():
    yj_clean_logs()
    print('yj_clean_logs()')
    return [
        gr.Textbox(value=""), # yj_query
        gr.Button(variant="secondary"), # yj_start_btn
        gr.Button(variant="secondary"), # yj_plan_btn
        gr.Textbox(value=""), # yj_context
        gr.Textbox(value=""), # yj_plan
    ]


##### btn, textbox
def chg_btn_color_if_input(_topic):
    if _topic:
        return gr.Button(variant="primary")
    else:
        return gr.Button(variant="secondary")

def chg_textbox_visible(_radio):
    if _radio == '快速':
        return {
            rag_ans1: gr.Textbox(visible=True),
            rag_log1: gr.Textbox(visible=True),
            rag_ans2: gr.Textbox(visible=False),
            rag_log2: gr.Textbox(visible=False),
            rag_ans3: gr.Textbox(visible=False),
            rag_log3: gr.Textbox(visible=False),
        }
    if _radio == '深思':
        return {
            rag_ans1: gr.Textbox(visible=False),
            rag_log1: gr.Textbox(visible=False),
            rag_ans2: gr.Textbox(visible=True),
            rag_log2: gr.Textbox(visible=True),
            rag_ans3: gr.Textbox(visible=False),
            rag_log3: gr.Textbox(visible=False),
        }
    if _radio == '多智':
        return {
            rag_ans1: gr.Textbox(visible=False),
            rag_log1: gr.Textbox(visible=False),
            rag_ans2: gr.Textbox(visible=False),
            rag_log2: gr.Textbox(visible=False),
            rag_ans3: gr.Textbox(visible=True),
            rag_log3: gr.Textbox(visible=True),
        }


##### RAG
def rag_handle_upload(_tmp_path):
    _tmp_files = []
    _out = []
    for i in _tmp_path:
        i_fp = i.name
        _tmp_files.append(i_fp)
        i_fn = os.path.basename(i_fp)
        i_dir = os.path.dirname(i_fp)
        # print(i_dir)
        i_md5 = calculate_md5(i_fp)
        # print(i_md5)
        i_fn_new = f"{i_md5}" + os.path.splitext(os.path.basename(i_fp))[1]
        i_fp_new = os.path.join(_upload_dir, i_fn_new)
        i_db_name = os.path.join(_upload_dir, f"{i_md5}_openai")
        # print(i_fp_new)
        if not os.path.exists(i_fp_new):
            logger_rag.info(f"upload {i_fn} to {i_fn_new}")
            dir_to_faiss_openai(i_dir, i_db_name, _clean_txt_dir)
            shutil.move(i_fp, i_fp_new)
            merge_faiss_openai(_db_name, i_db_name)
            shutil.rmtree(i_db_name)
            logger_rag.info(f"done upload process")
            _out.append(f"upload {i_fn} to {i_fn_new}")
        else:
            logger_rag.info(f"{i_fn} ({i_fn_new}) exists")
            _out.append(f"{i_fn} ({i_fn_new}) exists")
    return "\n".join(_out)


def qa_faiss_openai(_query, _vdb):
    start_time = time.time()
    _ans, _step, _token_cost = qa_vdb_multi_query(_query, _vdb, 'stuff')
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"Time: {execution_time:.1f} seconds"
    logger_rag.info(f"{_time}")
    return [_ans, _step, _token_cost, _time]

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


def rag_helper_fast(_query, _radio):
    _vdb = get_faiss_OpenAI(_db_name)
    _ans, _ref = "", ""
    write_log_ans(_log_ans1,'')
    write_log_ref(_log_ref1,'')
    if _radio == "快速":
        with cf.ProcessPoolExecutor() as executor:
            write_log_ans(_log_ans1, '', 'continue')
            _ans, _step, _token_cost, _time = qa_faiss_openai(_query, _vdb)
            _ref = f"{_token_cost}\n{_time}\n\n{_step}"
            write_log_ans(_log_ans1, clean_txt(_ans), 'done')
            write_log_ref(_log_ref1, _ref)
    return

def rag_helper_advanced(_query, _radio):
    _ans, _ref = "", ""
    write_log_ans(_log_ans2,'')
    write_log_ref(_log_ref2,'')
    if _radio == "深思":
        write_log_ans(_log_ans2, '', 'continue')
        start_time = time.time()
        _ans, _token_cost = bshr_vdb(_query, _db_name)
        print(_ans)
        end_time = time.time()
        execution_time = end_time - start_time
        _time = f"Time: {execution_time:.1f} seconds"
        _ref = f"{_token_cost}\n{_time}"
        write_log_ans(_log_ans2, clean_txt(_ans), 'done')
        write_log_ref(_log_ref2, _ref)
    return

def rag_helper_autogen(_query, _radio):
    _vdb = get_faiss_OpenAI(_db_name)
    _ans, _ref = "", ""
    write_log_ans(_log_ans3,'')
    write_log_ref(_log_ref3,'')
    if _radio == "多智":
        start_time = time.time()
        write_log_ans(_log_ans3, '', 'continue')
        # ChatCompletion.start_logging(reset_counter=True, compact=False)
        ### task list
        _task_list = create_rag_task_list_zh(_query)
        write_log_ans(_log_ans3, f"生成的子问题列表：\n\n{_task_list}", 'continue')
        end_time = time.time()
        execution_time = end_time - start_time
        _time = f"Time: {execution_time:.1f} seconds"
        write_log_ref(_log_ref3, f"\n\n{_time}")
        # print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")
        ### context
        _context = search_faiss_openai(_task_list, _vdb)
        write_log_ans(_log_ans3, f"生成的 QA 上下文：\n\n{_context}", 'continue')
        end_time = time.time()
        execution_time = end_time - start_time
        _time = f"Time: {execution_time:.1f} seconds"
        write_log_ref(_log_ref3, f"\n\n{_time}")
        ### qa
        _qa, _tc = qa_with_context_as_mio(_query, _context)
        write_log_ans(_log_ans3, f"生成的最终答案：\n\n{_qa}", 'done')
        end_time = time.time()
        execution_time = end_time - start_time
        _time = f"Time: {execution_time:.1f} seconds"
        write_log_ref(_log_ref3, f"\n\n{_time}\n\n{'='*40}\n\n{_context}")
    return

def rag_helper(_query, _radio):
    if _radio == "快速":
        logger_rag.info("[快速]")
        rag_helper_fast(_query, _radio)
    if _radio == "深思":
        logger_rag.info("[深思]")
        rag_helper_advanced(_query, _radio)
    if _radio == "多智":
        logger_rag.info("[多智]")
        rag_helper_autogen(_query, _radio)


##### ml
def ml_helper(_query):
    _ans, _ref = "", ""
    write_log_ans(_log_ans_ml,'')
    write_log_ref(_log_ref_ml,'')
    start_time = time.time()
    write_log_ans(_log_ans_ml, '', 'continue')
    # ChatCompletion.start_logging(reset_counter=True, compact=False)
    ### task list
    _task_list = create_jdml_task_list_zh(_query)
    write_log_ans(_log_ans_ml, f"{_task_list}", 'done')
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"Time: {execution_time:.1f} seconds"
    write_log_ref(_log_ref_ml, f"\n\n{_time}")


##### yj
_vdb_name = str(WORKSPACE_AUTOGEN / 'wf_jd')

def yj_sort_out_context(_event):
    write_log_ans(_log_ans_yj_context, '')
    start_time = time.time()
    write_log_ans(_log_ans_yj_context, '', 'continue')
    #####
    _query = generate_search_query_for_event(_event)
    generate_vdb_for_search_query(_query, _vdb_name)
    _context = generate_event_context(_event, _vdb_name)
    write_log_ans(_log_ans_yj_context, _context, 'done')
    #####
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"Time: {execution_time:.1f} seconds"
    add_log_ref(_log_ref_yj, _time)
    time.sleep(1)
    return gr.Button(variant="primary")
    

def yj_write_plan(_event, _context):
    write_log_ans(_log_ans_yj_plan, '')
    start_time = time.time()
    write_log_ans(_log_ans_yj_plan, '', 'continue')
    #####
    _plan = generate_event_plan(_event, _vdb_name, _context)
    write_log_ans(_log_ans_yj_plan, _plan, 'done')
    #####
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"Time: {execution_time:.1f} seconds"
    add_log_ref(_log_ref_yj, _time)


##### UI
_description = """
# 应急事件 / 报文问答 / 命令解析 / 标签提取
"""
chat_ask = gr.Textbox(label="", placeholder="...", lines=5, max_lines=5, interactive=True, visible=True, scale=9)

with gr.Blocks(title=_description) as demo:
    dh_history = gr.State([])
    dh_user_question = gr.State("")
    gr.Markdown(_description)

    with gr.Tab(label = "应急事件"):
        with gr.Row():
            with gr.Column(scale=1):
                yj_query = gr.Textbox(label="任务", placeholder="...", lines=10, max_lines=10, interactive=True, visible=True)
                yj_start_btn = gr.Button("搜集信息", variant="secondary", visible=True)
                yj_clean_btn = gr.Button("停止/清空", variant="secondary", visible=True)
            with gr.Column(scale=1):
                yj_log = gr.Textbox(label="日志", placeholder="...", lines=16, max_lines=16, interactive=False, visible=True)
        yj_context = gr.Textbox(label="事件脉络", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        yj_plan_btn = gr.Button("生成总结", variant="secondary", visible=True)
        yj_plan = gr.Textbox(label="总结报告", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        yj_query.change(
            chg_btn_color_if_input,
            [yj_query],
            [yj_start_btn]
        )
        yj_start_btn.click(
            yj_read_logs,
            [],
            [yj_log, yj_context, yj_plan],
            every=1
        )
        yj_start_btn.click(
            yj_sort_out_context,
            [yj_query],
            [yj_plan_btn]
        )
        yj_clean_btn.click(
            yj_clean_all,
            [],
            [yj_query, yj_start_btn, yj_plan_btn, yj_context, yj_plan]
        )
        yj_plan_btn.click(
            yj_write_plan,
            [yj_query, yj_context],
            []
        )


    with gr.Tab(label = "报文问答"):
        with gr.Row():
            rag_upload = gr.File(label="上传报文", file_count="multiple", type="file", interactive=True, visible=True)
            rag_tmp_files = gr.Textbox(label="上传日志", placeholder="...", lines=9, max_lines=9, interactive=False, visible=True)
        rag_query = gr.Textbox(label="提问", placeholder="...", lines=10, max_lines=10, interactive=True, visible=True)
        rag_radio = gr.Radio(
            # ["快速", "多智", "深思"],
            # label="快速(<半分钟), 多智(~2分钟), 深思(~4分钟)",
            ["快速", "多智"],
            label="快速(<半分钟), 多智(~2分钟)",
            info="",
            type="value",
            value="快速",
        )
        rag_start_btn = gr.Button("开始", variant="secondary", visible=True)
        rag_clean_btn = gr.Button("清空", variant="secondary", visible=True)
        with gr.Row():
            rag_ans1 = gr.Textbox(label="回答 (快速)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
            rag_ans2 = gr.Textbox(label="回答 (深思)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=False)
            rag_ans3 = gr.Textbox(label="回答 (多智)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=False)
        with gr.Row():
            rag_log1 = gr.Textbox(label="日志 (快速)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
            rag_log2 = gr.Textbox(label="日志 (深思)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=False)
            rag_log3 = gr.Textbox(label="日志 (多智)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=False)
        rag_upload.upload(
            rag_handle_upload,
            [rag_upload],
            [rag_tmp_files]
        )
        rag_radio.change(
            chg_textbox_visible,
            [rag_radio],
            [rag_ans1, rag_ans2, rag_log1, rag_log2, rag_ans3, rag_log3]
        )
        rag_query.change(
            chg_btn_color_if_input,
            [rag_query],
            [rag_start_btn]
        )
        rag_start_btn.click(
            rag_read_logs,
            [],
            [rag_ans1, rag_log1, rag_ans2, rag_log2, rag_ans3, rag_log3],
            every=1
        )
        rag_start_btn.click(
            rag_helper,
            [rag_query, rag_radio],
            []
        )
        rag_clean_btn.click(
            rag_clean_all,
            [],
            [rag_query, rag_start_btn]
        )
 

    with gr.Tab(label = "命令解析"):
        ml_query = gr.Textbox(label="命令", placeholder="...", lines=10, max_lines=10, interactive=True, visible=True)
        ml_start_btn = gr.Button("开始", variant="secondary", visible=True)
        ml_clean_btn = gr.Button("清空", variant="secondary", visible=True)
        ml_ans = gr.Textbox(label="解析", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        ml_log = gr.Textbox(label="日志", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        ml_query.change(
            chg_btn_color_if_input,
            [ml_query],
            [ml_start_btn]
        )
        ml_start_btn.click(
            ml_read_logs,
            [],
            [ml_ans, ml_log],
            every=1
        )
        ml_start_btn.click(
            ml_helper,
            [ml_query],
            []
        )
        ml_clean_btn.click(
            ml_clean_all,
            [],
            [ml_query, ml_start_btn]
        )

    with gr.Tab(label = "标签提取"):
        with gr.Row():
            upload_box = gr.File(label="上传单个TXT", file_count="single", type="file", file_types=['.txt'], interactive=True)
            input_content = gr.Textbox(label="TXT文件内容", placeholder="...", lines=9, max_lines=9, interactive=False)
        start_btn = gr.Button("开始分析", variant="secondary")
        output_JQ = gr.Textbox(label="分析结果", placeholder="...", lines=10, interactive=False)    
        with gr.Row():
            # output_log = gr.Textbox(label="日志", placeholder="日志", lines=12, interactive=False)
            download_JQ = gr.File(label="下载分析", file_count="single", type="file", file_types=['.txt'], interactive=True, visible=False)
        upload_box.change(
            read_file,
            inputs=[upload_box],
            outputs=[input_content]
        )
        upload_box.change(
            chg_btn_color_if_file,
            inputs=[upload_box],
            outputs=[start_btn]
        )
        start_btn.click(
            run_llm_JQ,
            inputs=[upload_box],
            outputs=[output_JQ]
        )
        output_JQ.change(
            show_JQ_file,
            inputs=[output_JQ],
            outputs=[download_JQ]
        )

    # with gr.Tab(label = "聊天"):
    #     gr.ChatInterface(
    #         fn=chat_predict_openai,
    #         textbox=chat_ask,
    #         submit_btn="提交",
    #         stop_btn="停止",
    #         retry_btn="🔄 重试",
    #         undo_btn="↩️ 撤消",
    #         clear_btn="🗑️ 清除",
    #     )
    


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

