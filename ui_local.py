import sys
import urllib3
urllib3.disable_warnings()
import gradio as gr
# from functools import partial

from ui_local_rag import (
    rag_handle_upload,
    rag_read_logs,
    rag_helper,
    rag_clean_all,
)

from ui_local_tag import (
    read_file,
    parse_txt,
    show_JQ_file,
)

from ui_local_yj import (
    yj_read_logs,
    yj_sort_out_context_textgen,
    yj_clean_all,
    yj_write_plan,
    show_yj_context,
)


from ui_local_ct import (
    ct_read_logs,
    ct_sort_out_context_textgen,
    ct_clean_all,
    ct_write_plan,
    show_ct_context,
)


def chg_btn_color_if_input(input):
    if input:
        return gr.Button(variant="primary")
    else:
        return gr.Button(variant="secondary")


def chg_textbox_visible(_radio):
    if _radio == '快速':
        return {
            rag_ans_fast: gr.Textbox(visible=True),
            rag_log_fast: gr.Textbox(visible=True),
            rag_ans_autogen: gr.Textbox(visible=False),
            rag_log_autogen: gr.Textbox(visible=False),
        }
    if _radio == '多智':
        return {
            rag_ans_fast: gr.Textbox(visible=False),
            rag_log_fast: gr.Textbox(visible=False),
            rag_ans_autogen: gr.Textbox(visible=True),
            rag_log_autogen: gr.Textbox(visible=True),
        }


##### UI
_description = """
# 报文问答 / 标签提取 / 事件脉络
"""
chat_ask = gr.Textbox(label="", placeholder="...", lines=5, max_lines=5, interactive=True, visible=True, scale=9)

with gr.Blocks(title=_description) as demo:
    dh_history = gr.State([])
    dh_user_question = gr.State("")
    gr.Markdown(_description)


    with gr.Tab(label = "报文问答"):
        with gr.Row():
            rag_upload = gr.File(label="上传TXT", file_count="multiple", type="file", file_types=['.txt'], interactive=True, visible=True)
            rag_tmp_files = gr.Textbox(label="上传日志", placeholder="...", lines=9, max_lines=9, interactive=False, visible=True)
        rag_query = gr.Textbox(label="提问", placeholder="...", lines=10, max_lines=10, interactive=True, visible=True)
        rag_radio = gr.Radio(
            # ["快速"],
            # label="快速(~1分钟)",
            ["快速", "多智"],
            label="快速(~1分钟), 多智(~2分钟)",
            info="",
            type="value",
            value="快速",
        )
        rag_start_btn = gr.Button("开始", variant="secondary", visible=True)
        rag_clean_btn = gr.Button("清空", variant="secondary", visible=True)
        with gr.Row():
            rag_ans_fast = gr.Textbox(label="回答 (快速)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
            rag_ans_autogen = gr.Textbox(label="回答 (多智)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=False)
        with gr.Row():
            rag_log_fast = gr.Textbox(label="日志 (快速)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=True)
            rag_log_autogen = gr.Textbox(label="日志 (多智)", placeholder="...", lines=15, max_lines=15, interactive=False, visible=False)
        rag_upload.upload(
            rag_handle_upload,
            [rag_upload],
            [rag_tmp_files]
        )
        rag_radio.change(
            chg_textbox_visible,
            [rag_radio],
            [rag_ans_fast, rag_log_fast, rag_ans_autogen, rag_log_autogen]
        )
        rag_query.change(
            chg_btn_color_if_input,
            [rag_query],
            [rag_start_btn]
        )
        rag_start_btn.click(
            rag_read_logs,
            [],
            [rag_ans_fast, rag_log_fast, rag_ans_autogen, rag_log_autogen],
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
 

    with gr.Tab(label = "标签提取"):
        with gr.Row():
            upload_box = gr.File(label="上传TXT", file_count="single", type="file", file_types=['.txt'], interactive=True)
            input_content = gr.Textbox(label="TXT内容", placeholder="...", lines=9, max_lines=9, interactive=True)
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
        input_content.change(
            chg_btn_color_if_input,
            inputs=[input_content],
            outputs=[start_btn]
        )
        start_btn.click(
            parse_txt,
            inputs=[input_content],
            outputs=[output_JQ]
        )
        output_JQ.change(
            show_JQ_file,
            inputs=[output_JQ],
            outputs=[download_JQ]
        )


    with gr.Tab(label = "应急事件"):
        with gr.Row():
            with gr.Column(scale=1):
                yj_query = gr.Textbox(label="专题", placeholder="...", lines=8, max_lines=8, interactive=True, visible=True)
                yj_start_btn = gr.Button("开始梳理", variant="secondary", visible=True)
                yj_clean_btn = gr.Button("清空", variant="secondary", visible=True)
            with gr.Column(scale=1):
                yj_log = gr.Textbox(label="日志", placeholder="...", lines=14, max_lines=14, interactive=False, visible=True)
        yj_context = gr.Textbox(label="事件脉络", placeholder="...", lines=18, max_lines=18, interactive=False, visible=True)
        yj_plan_btn = gr.Button("生成总结", variant="secondary", visible=False)
        yj_plan = gr.Textbox(label="总结报告", placeholder="...", lines=15, max_lines=15, interactive=False, visible=False)
        yj_download_context = gr.File(label="下载文件", file_count="single", type="file", file_types=['.md'], interactive=True, visible=False)
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
            yj_sort_out_context_textgen,
            [yj_query],
            [yj_plan_btn]
        )
        yj_clean_btn.click(
            yj_clean_all,
            [],
            [yj_query, yj_start_btn, yj_plan_btn, yj_log, yj_context, yj_plan]
        )
        yj_plan_btn.click(
            yj_write_plan,
            [yj_query, yj_context],
            []
        )
        yj_context.change(
            show_yj_context,
            inputs=[yj_context],
            outputs=[yj_download_context]
        )


    with gr.Tab(label = "冲突事件"):
        with gr.Row():
            with gr.Column(scale=1):
                ct_query = gr.Textbox(label="专题", placeholder="...", lines=8, max_lines=8, interactive=True, visible=True)
                ct_start_btn = gr.Button("开始梳理", variant="secondary", visible=True)
                ct_clean_btn = gr.Button("清空", variant="secondary", visible=True)
            with gr.Column(scale=1):
                ct_log = gr.Textbox(label="日志", placeholder="...", lines=14, max_lines=14, interactive=False, visible=True)
        ct_context = gr.Textbox(label="事件脉络", placeholder="...", lines=18, max_lines=18, interactive=False, visible=True)
        ct_plan_btn = gr.Button("生成总结", variant="secondary", visible=False)
        ct_plan = gr.Textbox(label="总结报告", placeholder="...", lines=15, max_lines=15, interactive=False, visible=False)
        ct_download_context = gr.File(label="下载文件", file_count="single", type="file", file_types=['.md'], interactive=True, visible=False)
        ct_query.change(
            chg_btn_color_if_input,
            [ct_query],
            [ct_start_btn]
        )
        ct_start_btn.click(
            ct_read_logs,
            [],
            [ct_log, ct_context, ct_plan],
            every=1
        )
        ct_start_btn.click(
            ct_sort_out_context_textgen,
            [ct_query],
            [ct_plan_btn]
        )
        ct_clean_btn.click(
            ct_clean_all,
            [],
            [ct_query, ct_start_btn, ct_plan_btn, ct_log, ct_context, ct_plan]
        )
        ct_plan_btn.click(
            ct_write_plan,
            [ct_query, ct_context],
            []
        )
        ct_context.change(
            show_ct_context,
            inputs=[ct_context],
            outputs=[ct_download_context]
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
            demo.queue().launch(
                server_name="0.0.0.0",
                server_port=_port,
                share=False,
                favicon_path="./asset/favicon_paper.png",
                ssl_verify=False,
            )
        except Exception as e:
            print(f"{e}")
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

