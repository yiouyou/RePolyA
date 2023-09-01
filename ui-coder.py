import gradio as gr
from repolya.coder import parsesource
from repolya._const import WORKSPACE_ROOT
from repolya._log import logger_chat


def chg_btn_color_if_input(_input):
    import gradio as gr
    if _input:
        return gr.update(variant="primary")
    else:
        return gr.update(variant="secondary")


def _selected_lang(_query, _radio):
    _ans, _steps = "", ""
    if _radio in ["c", "csharp", "golang", "java", "js", "python", "rust", "lua"]:
        _ans, _steps = parsesource(_query, _radio)
    else:
        _ans = f"ERROR: not supported {_radio}"
    return [_ans, _steps]


##### UI
_description = """
# Assistant
"""
with gr.Blocks(title=_description) as demo:
    gr.Markdown(_description)

    with gr.Tab(label = "Code Digester"):
        _folder = gr.Textbox(label="Folder", placeholder="Folder", interactive=True, visible=True)
        _radio = gr.Radio(
            ["c", "csharp", "golang", "java", "js", "python", "rust", "lua"],
            label="Which language do you want to digest?",
            info="",
            type="value",
            value="js"
        )
        _start_btn = gr.Button("Start", variant="secondary", visible=True)
        _ans = gr.Textbox(label="Ans", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        _steps = gr.Textbox(label="Steps", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
        _folder.change(
            chg_btn_color_if_input,
            [_folder],
            [_start_btn]
        )
        _start_btn.click(
            _selected_lang,
            [_folder, _radio],
            [_ans, _steps]
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

