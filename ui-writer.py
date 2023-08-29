import sys
import urllib3
urllib3.disable_warnings()
import gradio as gr
from functools import partial
from repolya.writer import generated_text
from repolya._log import logger_writer
from repolya._const import LOG_ROOT
_writer_log = LOG_ROOT / 'writer.log'


def chg_btn_color_if_input(_topic):
    if _topic:
        return gr.update(variant="primary")
    else:
        return gr.update(variant="secondary")

##### writing assistant
def auto_wa(_topic):
    with open(_writer_log, 'w', encoding='utf-8') as wf:
        wf.write('')
    _text, _file = generated_text(_topic)
    return [_text, gr.update(value=_file)]


# class Logger:
#     def __init__(self, filename):
#         self.terminal = sys.stdout
#         self.log = open(filename, "w")
#     def write(self, message):
#         self.terminal.write(message)
#         self.log.write(message)
#     def flush(self):
#         self.terminal.flush()
#         self.log.flush()
#     def isatty(self):
#         return False
# sys.stdout = Logger(_writer_log)


def read_logs():
    # sys.stdout.flush()
    ### read log
    with open(_writer_log, "r") as f:
        _log = f.read()
    return _log


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
        wa_start_btn.click(
            read_logs,
            [],
            [wa_steps],
            every=1
        )
        # demo.load(
        #     read_logs,
        #     [],
        #     [wa_steps],
        #     every=1
        # )


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
        # ssl_keyfile="./ssl/key.pem",
        # ssl_certfile="./ssl/cert.pem",
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

