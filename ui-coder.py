import os
from zipfile import ZipFile
import gradio as gr
from repolya.coder import parsesource
from repolya._const import WORKSPACE_ROOT
from repolya._log import logger_chat
from repolya._const import LOG_ROOT
_coder_log = LOG_ROOT / 'coder.log'


def chg_btn_color_if_input(_input):
    import gradio as gr
    if _input:
        return gr.update(variant="primary")
    else:
        return gr.update(variant="secondary")


def handle_zip(_tmp_path):
    _unzip_dir = ""
    _fs = []
    if len(_tmp_path) == 1:
        _zp = _tmp_path[0]
        _zn = _zp.name
        _fn, _ext = os.path.splitext(os.path.basename(_zn))
        _unzip_dir = os.path.join(os.path.dirname(_zn), _fn)
        with ZipFile(_zn, 'r') as zfile:
            zfile.extractall(_unzip_dir)
            for zinfo in zfile.infolist():
                _fs.append(
                    {
                        "name": zinfo.filename,
                        "file_size": zinfo.file_size,
                        "compressed_size": zinfo.compress_size,
                    }
                )
    else:
        raise gr.Error("ERROR: can only upload ONE zip file")
    return _unzip_dir, _fs


def _selected_lang(_query, _radio):
    _wfn = ""
    if _radio in ["c", "csharp", "golang", "java", "js", "python", "rust", "lua"]:
        _wfn = parsesource(_query, _radio)
    else:
        raise gr.Error(f"ERROR: not supported {_radio}")
    return _wfn


def read_logs():
    ### read log
    with open(_coder_log, "r") as f:
        _log = f.read()
    return _log


##### UI
_description = """
# Assistant
"""
with gr.Blocks(title=_description) as demo:
    gr.Markdown(_description)
    _unzip_dir = gr.State("")
    _fs = gr.State([])

    with gr.Tab(label = "Code Digester"):
        _upload = gr.File(label="Upload a ZIP file", file_count="multiple", type="file", interactive=True, visible=True)
        _radio = gr.Radio(
            ["c", "csharp", "golang", "java", "js", "python", "rust", "lua"],
            label="Which language do you want to digest?",
            info="",
            type="value",
            value="js"
        )
        _start_btn = gr.Button("Start", variant="secondary", visible=True)
        _ans = gr.File()
        _steps = gr.Textbox(label="Steps", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        _upload.upload(
            handle_zip,
            [_upload],
            [_unzip_dir, _fs]
        )
        _upload.change(
            chg_btn_color_if_input,
            [_upload],
            [_start_btn]
        )
        _start_btn.click(
            _selected_lang,
            [_unzip_dir, _radio],
            [_ans]
        )
        _start_btn.click(
            read_logs,
            [],
            [_steps],
            every=1
        )


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

