# coding=utf-8
import sys
# from dotenv import load_dotenv
# load_dotenv()
import urllib3
urllib3.disable_warnings()
import gradio as gr
from functools import partial
from council_writing_assistant import generated_text, LOG_ROOT
from paper import querypapers
from paper import qadocs


def chg_btn_color_if_input(_topic):
    if _topic:
        return gr.update(variant="primary")
    else:
        return gr.update(variant="secondary")

##### writing assistant
def auto_wa(_topic):
    with open(_log_path, 'w', encoding='utf-8') as wf:
        wf.write('')
    _text, _file = generated_text(_topic)
    return [_text, gr.update(value=_file)]

class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        
    def flush(self):
        self.terminal.flush()
        self.log.flush()
        
    def isatty(self):
        return False

_log_path = LOG_ROOT / 'wa.log'
sys.stdout = Logger(_log_path)

def read_logs():
    sys.stdout.flush()
    ### read log
    with open(_log_path, "r") as f:
        _log = f.read()
    return _log


##### search/fetch/ask
def search_topic_papers(_topic):
    papers = []
    _papers = querypapers(_topic, 5)
    for i in sorted(_papers.keys()):
        print(f"{'-'*40}\n{i}\n{'-'*40}")
        for j in sorted(_papers[i].keys()):
            print(f"{j}: {_papers[i][j]}")
        _i = {
            "title": _papers[i]['title'],
            "doi": _papers[i]['doi'],
            "citationCount:": _papers[i]['citationCount:'],
            "year": _papers[i]['year'],
            "file": i
        }
        papers.append(_i)
        print("\n")
    return papers

def your_answer_function(_ask):
    # 使用虚拟的数据，返回问题的回答
    return "Answer to the question based on papers"

def search_topic(_topic):
    res = []
    papers = []
    if not _topic:
        raise gr.Error("请先输入'研究主题'")
    else:
        papers = search_topic_papers(_topic)
        for i in papers:
            title = i['title']
            res.append(title)
    return [gr.update(choices=res), papers]

def show_last_meta(_checkbox, _papers):
    _titles = [_checkbox[-1]]
    # print(_titles)
    _meta = []
    for i in _titles:
        for j in _papers:
            if i == j['title']:
                _meta.append(f"\ncitationCount: {j['citationCount']}\nurl: {j['url']}\nbibtex: {j['bibtex']}\n")
                break
    return "".join(_meta)

def fetch_selected_pdf(_checkbox, _papers):
    _fp = []
    if _checkbox is None:
        raise gr.Error("请先选取'相关文献'")
    else:
        for i in _checkbox:
            for j in _papers:
                if i == j['title']:
                    _fp.append(j['pdf'])
    return gr.update(value=_fp)

def search_topic_papers(_topic):
    papers = []
    _papers = querypapers(_topic, 5)
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
    print(papers)
    return papers

def answer_question(_ask, _pdf):
    _ans = "Answer to the question based on papers"
    _res = qadocs(_ask, _pdf)
    _ans = _res.formatted_answer
    return _ans


##### UI
_description = """
# Assistant
"""
with gr.Blocks(title=_description) as demo:
    gr.Markdown(_description)

    with gr.Tab(label = "写作助手"):
        with gr.Row(equal_height=True):
            wa_topic = gr.Textbox(label="主题", placeholder="Topic", lines=8, max_lines=8, interactive=True, visible=True)
            download_box = gr.File(label="下载", file_count="single", type="file", file_types=['.md'], interactive=False)
            # wa_file = gr.File(label="Generated Files", file_count="multiple", type="file", interactive=False, visible=True)
        wa_start_btn = gr.Button("开始", variant="secondary", visible=True)
        wa_txt = gr.Textbox(label="Markdown", placeholder="...", lines=10, max_lines=10, interactive=False, visible=True)
        wa_steps = gr.Textbox(label="log", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        wa_topic.change(
            chg_btn_color_if_input,
            [wa_topic],
            [wa_start_btn]
        )
        wa_start_btn.click(
            auto_wa,
            [wa_topic],
            [wa_txt, download_box]
        )
        demo.load(
            read_logs,
            [],
            [wa_steps],
            every=1
        )

    _papers = gr.State([])
    with gr.Tab(label="输入研究主题，获取相关文献，根据文献问答问题"):
        _topic = gr.Textbox(label="研究主题")
        _btn_search = gr.Button("搜索")
        with gr.Row(equal_height=True):
            _papers_tile = gr.CheckboxGroup(label="相关文献")
            _papers_meta = gr.Textbox(label="文献信息")
        _btn_select = gr.Button("获取PDF")
        _pdf = gr.File(label="已获取", file_count="single", type="file", file_types=['.pdf'], interactive=False)
        _ask = gr.Textbox(label="问题")
        _btn_ask = gr.Button("提问")
        _ans = gr.Textbox(label="回答")
        _topic.change(
            chg_btn_color_if_input,
            [_topic],
            [_btn_search]
        )
        _btn_search.click(
            search_topic,
            [_topic],
            [_papers_tile, _papers]
        )
        _papers_tile.select(
            show_last_meta,
            [_papers_tile, _papers],
            [_papers_meta]
        )
        _btn_select.click(
            fetch_selected_pdf,
            [_papers_tile, _papers],
            [_pdf]
        )
        _ask.change(
            chg_btn_color_if_input,
            [_ask],
            [_btn_ask]
        )
        _btn_ask.click(
            answer_question,
            [_ask, _pdf],
            [_ans]
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

    _port = int(sys.argv[1])
    demo.queue(concurrency_count=1).launch(
        server_name="0.0.0.0",
        server_port=_port,
        share=False,
        favicon_path="./asset/favicon_wa.png",
        # auth = ('sz','1123'),
        # auth_message= "欢迎回来！",
        ssl_verify=False,
        # ssl_keyfile="./localhost+2-key.pem",
        # ssl_certfile="./localhost+2.pem",
        ssl_keyfile="./ssl/key.pem",
        ssl_certfile="./ssl/cert.pem",
    )

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

