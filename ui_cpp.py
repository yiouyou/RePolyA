import sys, os
import urllib3
urllib3.disable_warnings()
import gradio as gr
# from functools import partial

from repolya.chat import chat_predict_openai
from repolya.paper.querypapers import querypapers
from repolya.paper.qadocs import qadocs
# from repolya.writer import generated_text
from repolya.paper.digestpaper import (
    digest_pdf,
    qa_pdf,
    sum_pdf,
    ans_qlist,
)

from repolya._log import logger_paper
from repolya._const import LOG_ROOT, PAPER_PDF
_writer_log = LOG_ROOT / 'writer.log'


def chg_btn_color_if_input(_topic):
    if _topic:
        return gr.update(variant="primary")
    else:
        return gr.update(variant="secondary")

def chg_btn_color_if_clear():
    return gr.update(variant="secondary")

def clean_text_if_clear():
    return "", "", "", ""

##### search/fetch/ask
def search_topic_papers(_topic, _N):
    papers = []
    _papers = querypapers(_topic, _N)
    # print("search_topic_papers", _papers)
    if _papers:
        for i in sorted(_papers.keys()):
            print(f"{'-'*40}\n{i}\n{'-'*40}")
            for j in sorted(_papers[i].keys()):
                print(f"{j}: {_papers[i][j]}")
            _i = {
                "title": _papers[i]['title'],
                "bibtex": _papers[i]['bibtex'],
                "doi": _papers[i]['doi'],
                "citationCount": _papers[i]['citationCount'],
                "year": _papers[i]['year'],
                "url": _papers[i]['url'],
                "pdf": i
            }
            papers.append(_i)
            print("\n")
    return papers

def search_topic(_topic, _N):
    logger_paper.info(f"topic: '{_topic}'")
    _res = []
    _papers = []
    if not _topic:
        raise gr.Error("请先输入'研究主题'")
    else:
        _papers = search_topic_papers(_topic, _N)
        for i in _papers:
            title = i['title']
            doi = i['doi']
            _res.append(f"{title} [{doi}]")
            logger_paper.info(f"{title} [{doi}]")
    return [gr.update(choices=_res), _papers]

def find_field(pattern, text):
    _txt = ""
    import re
    _m = re.search(pattern, text)
    if _m:
        _txt = _m.group(1).strip()
    return _txt

def parse_bibtex_au_jo_bo(_bibtex):
    _txt = []
    _author = find_field(r'author\s*=\s*{(.*?)}', _bibtex)
    _journal = find_field(r'journal\s*=\s*{(.*?)}', _bibtex)
    _booktitle = find_field(r'booktitle\s*=\s*{(.*?)}', _bibtex)
    journal = ""
    if _journal and _booktitle:
        if _journal.lower() == _booktitle.lower():
            journal = f"Journal: {_journal}"
        else:
            journal = f"Journal: {_journal}, Booktitle: {_booktitle}"
    _txt.append(journal)
    if _author:
        _txt.append(f"Author: {_author}")
    return "\n\n".join(_txt)

def show_last_meta(_checkbox, _papers):
    _titles = [_checkbox[-1]]
    # print(_titles)
    _meta = []
    for i in _titles:
        for j in _papers:
            # i is 'title [doi]'
            if j['title'] in i:
                i_txt = parse_bibtex_au_jo_bo(j['bibtex'])
                i_meta = f"\n[citationCount]\n{j['citationCount']}\n\n[bibtex]\n{i_txt}\n"
                _meta.append(i_meta)
                break
    return "".join(_meta)

def fetch_selected_pdf(_checkbox, _papers):
    _fp = []
    if _checkbox is None:
        raise gr.Error("请先选取'相关文献'")
    else:
        # for i in _checkbox:
        #     for j in _papers:
        #         # i is 'title [doi]'
        #         if j['title'] in i:
        #             _fp.append(j['pdf'])
        for i in _papers:
            _fp.append(i['pdf'])
    return gr.update(value=_fp), _fp

def answer_question(_ask, _pdf):
    logger_paper.info(f"ask: '{_ask}'")
    _ans = "Answer to the question based on papers"
    _res = qadocs(_ask, _pdf)
    _ans = _res.formatted_answer
    _context = _res.context
    logger_paper.info(f"formatted_answer: '{_ans}'")
    logger_paper.info(f"context: '{_context}'")
    return _ans, _context


##### pdf
def jd_digest_pdf(_tmp_path):
    _tmp_pdf = ""
    if len(_tmp_path) == 1:
        _fp = _tmp_path[0].name
        logger_paper.info(_fp)
        digest_pdf(_fp)
        _tmp_pdf = _fp
    else:
        raise gr.Error("ERROR: can only upload ONE pdf file")
    return _tmp_pdf

def jd_sum_pdf(_tmp_pdf, _type):
    _sum, _sum_steps = "", ""
    _chain_type = "stuff"
    if _type == "精准":
        _chain_type = "refine"
    _sum, _sum_steps = sum_pdf(_tmp_pdf, _chain_type)
    return _sum, _sum_steps

def jd_ans_qlist(_tmp_pdf):
    _digest, _digest_steps = "", ""
    _digest, _digest_steps = ans_qlist(_tmp_pdf)
    return _digest, _digest_steps

def jd_qa_pdf(_tmp_pdf, _ask):
    _ans, _steps = "", ""
    _ans, _steps = qa_pdf(_tmp_pdf, _ask)
    return _ans, _steps


# ##### writing assistant
# def auto_wa(_topic):
#     with open(_writer_log, 'w', encoding='utf-8') as wf:
#         wf.write('')
#     _text, _file = generated_text(_topic)
#     return [_text, gr.update(value=_file)]

# def read_logs():
#     ### read log
#     with open(_writer_log, "r") as f:
#         _log = f.read()
#     return _log

##### UI
_description = """
# Assistant
"""
chat_ask = gr.Textbox(label="", placeholder="...", lines=5, max_lines=5, interactive=True, visible=True, scale=9)

with gr.Blocks(title=_description) as demo:
    gr.Markdown(_description)
    fd_papers = gr.State([])
    fd_PDFs = gr.State([])

    with gr.Tab(label = "Chat4"):
        
        gr.ChatInterface(
            fn=chat_predict_openai,
            textbox=chat_ask,
            submit_btn="提交",
            stop_btn="停止",
            retry_btn="🔄 重试",
            undo_btn="↩️ 撤消",
            clear_btn="🗑️ 清除",
        )

    with gr.Tab(label="泛读（主题/文献/问答）"):
        with gr.Row():
            fd_topic = gr.Textbox(label="研究主题")
            fd_N = gr.Slider(5, 10, value=5, step=1, label="大约数目", info="")
        search_btn = gr.Button("1.搜索")
        with gr.Row(equal_height=True):
            fd_papers_tile = gr.CheckboxGroup(label="相关文献")
            fd_papers_meta = gr.Textbox(label="文献信息")
        fd_select_btn = gr.Button("2.获取PDF")
        fd_downloaded_pdf = gr.File(label="已获取", file_count="single", type="file", file_types=['.pdf'], interactive=False)
        fd_ask = gr.Textbox(label="问题（英文问，英文答；中文问，中文答）")
        fd_ask_btn = gr.Button("3.提问")
        fd_ans = gr.Textbox(label="回答", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        fd_context = gr.Textbox(label="引文", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        fd_topic.change(
            chg_btn_color_if_input,
            [fd_topic],
            [search_btn]
        )
        search_btn.click(
            search_topic,
            [fd_topic, fd_N],
            [fd_papers_tile, fd_papers]
        )
        fd_papers_tile.change(
            chg_btn_color_if_input,
            [fd_papers_tile],
            [fd_select_btn]
        )
        fd_papers_tile.select(
            show_last_meta,
            [fd_papers_tile, fd_papers],
            [fd_papers_meta]
        )
        fd_select_btn.click(
            fetch_selected_pdf,
            [fd_papers_tile, fd_papers],
            [fd_downloaded_pdf, fd_PDFs]
        )
        fd_ask.change(
            chg_btn_color_if_input,
            [fd_ask],
            [fd_ask_btn]
        )
        fd_ask_btn.click(
            answer_question,
            [fd_ask, fd_PDFs],
            [fd_ans, fd_context]
        )

    with gr.Tab(label="精读（解析/总结/问答）"):
        jd_upload = gr.File(label="Upload a PDF file", file_count="multiple", type="file", interactive=True, visible=True)
        jd_radio = gr.Radio(
            ["快速", "精准"],
            label="分析模式",
            info="",
            type="value",
            value="快速"
        )
        jd_tmp_pdf = gr.Textbox(label="digest", visible=False)
        jd_qlist_btn = gr.Button("开始解析", variant="secondary", visible=True)
        jd_qlist = gr.Textbox(label="Digest|文章解析", placeholder="...", lines=15, max_lines=10, interactive=False, visible=True)
        jd_sum_btn = gr.Button("开始总结", variant="secondary", visible=True)
        jd_sum = gr.Textbox(label="Summary|文章总结", placeholder="...", lines=15, max_lines=10, interactive=False, visible=True)
        with gr.Row():
            jd_ask = gr.Textbox(label="问题（英文问，英文答；中文问，中文答）")
        jd_ask_btn = gr.Button("提问")
        jd_ans = gr.Textbox(label="回答", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        jd_steps = gr.Textbox(label="Log", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        jd_upload.upload(
            jd_digest_pdf,
            [jd_upload],
            [jd_tmp_pdf]
        )
        jd_upload.clear(
            chg_btn_color_if_clear,
            [],
            [jd_sum_btn]
        )
        jd_upload.clear(
            chg_btn_color_if_clear,
            [],
            [jd_qlist_btn]
        )
        jd_upload.clear(
            clean_text_if_clear,
            [],
            [jd_sum, jd_qlist, jd_ans, jd_steps]
        )
        jd_tmp_pdf.change(
            chg_btn_color_if_input,
            [jd_tmp_pdf],
            [jd_qlist_btn]
        )
        jd_qlist_btn.click(
            jd_ans_qlist,
            [jd_tmp_pdf],
            [jd_qlist, jd_steps]
        )
        jd_tmp_pdf.change(
            chg_btn_color_if_input,
            [jd_tmp_pdf],
            [jd_sum_btn]
        )
        jd_sum_btn.click(
            jd_sum_pdf,
            [jd_tmp_pdf, jd_radio],
            [jd_sum, jd_steps]
        )
        jd_ask.change(
            chg_btn_color_if_input,
            [jd_ask],
            [jd_ask_btn]
        )
        jd_ask_btn.click(
            jd_qa_pdf,
            [jd_tmp_pdf, jd_ask],
            [jd_ans, jd_steps]
        )


    # with gr.Tab(label = "写作助手"):
    #     with gr.Row(equal_height=True):
    #         wa_topic = gr.Textbox(label="主题", placeholder="Topic", lines=8, max_lines=8, interactive=True, visible=True)
    #         download_box = gr.File(label="下载", file_count="single", type="file", file_types=['.md'], interactive=False)
    #         # wa_file = gr.File(label="Generated Files", file_count="multiple", type="file", interactive=False, visible=True)
    #     wa_start_btn = gr.Button("开始", variant="secondary", visible=True)
    #     wa_txt = gr.Textbox(label="Markdown", placeholder="...", lines=10, max_lines=10, interactive=False, visible=True)
    #     wa_steps = gr.Textbox(label="log", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
    #     wa_topic.change(
    #         chg_btn_color_if_input,
    #         [wa_topic],
    #         [wa_start_btn]
    #     )
    #     wa_start_btn.click(
    #         auto_wa,
    #         [wa_topic],
    #         [wa_txt, download_box]
    #     )
    #     wa_start_btn.click(
    #         read_logs,
    #         [],
    #         [wa_steps],
    #         every=1
    #     )


# from fastapi import FastAPI, Response
# app = FastAPI()
# @app.get("/health")
# def index():
#     return {"message": "active"}
# app = gr.mount_gradio_app(app, demo.queue(concurrency_count=1), path="/")
# # uvicorn ui_cpp:app --host 0.0.0.0 --port 8899 --reload


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
                favicon_path="./asset/favicon_wa.png",
                # auth = ('sz','1123'),
                # auth_message= "欢迎回来！",
                ssl_verify=False,
                # ssl_keyfile="./ssl/key.pem",
                # ssl_certfile="./ssl/cert.pem",
            )
        except Exception as e:
            logger_paper.error(f"{e}")
            continue

    # import uvicorn
    # uvicorn.run(
    #     app,
    #     host="0.0.0.0",
    #     port=_port,
    #     ssl_keyfile="./ssl/key.pem",
    #     ssl_certfile="./ssl/cert.pem",
    #     reload=True,
    #     debug=True
    # )

