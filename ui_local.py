import sys, re
import urllib3
urllib3.disable_warnings()
import gradio as gr
# from functools import partial
import concurrent.futures as cf
import threading
import time
import shutil
import ast
import os
import re

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
    generate_search_dict_for_event,
    generate_event_context,
    generate_event_plan,
    clean_filename,
)
from repolya._const import LOG_ROOT, WORKSPACE_RAG, AUTOGEN_JD
from repolya._log import logger_rag, logger_yj
# from autogen import ChatCompletion

from ui_rag_JQ import JQ_openai_tagging


##### tagging
def read_file(file):
    if file:
        with open(file.name, encoding="utf-8") as f:
            content = f.read()
            return content

def chg_btn_color_if_input(input):
    if input:
        return gr.Button(variant="primary")
    else:
        return gr.Button(variant="secondary")


def call_yi(_sentence):
    model_url = "http://127.0.0.1:4442"
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    from langchain.llms import TextGen
    # langchain.debug = True
    llm = TextGen(
        model_url=model_url,
        temperature=0.01,
        max_new_tokens=250, # 250/2500
        # stop=["\nHuman:", "\n```\n"],
        # verbose=True,
    )
    _t1 = """### System:

假定你是情报分析员，请从给定新闻句子中，抽取如下实体：'时间'，'地点'，'人物'，'军队'，'武器'，'伤亡'。下面是一些csv格式的新闻句子分析示例，其中新闻句子已用双引号括起来，逗号后面是句子的分析结果：

"202306032020，乌克兰防空部队编号11316部队，在奥德赛市奥德赛特镇检测到导弹袭击，立即分析上报。", {"时间":"202306032020", "地点":"奥德赛市奥德赛特镇", "人物": "", "军队":"乌克兰防空部队编号11316部队", "武器": "", "伤亡": ""}

"202306032025，导弹在乌克兰基辅市沙拉克镇发生爆炸，造成两座大楼炸毁，约160名平民伤亡。", {"时间":"202306032025", "地点":"基辅市沙拉克镇", "人物": "", "军队":"", "武器": "", "伤亡":"160名平民伤亡"}

"202306032025，乌克兰军事指挥中心瓦列里·扎卢日内将军，做出紧急预案，《军事入侵防御紧急方案》（乌-防空10586号），命令乌克兰陆军部队编号11316部队，乌克兰陆军部队编号11316部队，立即做出应对措施，立即处理。", {"时间":"202306032025", "地点": "", "人物":"瓦列里·扎卢日内将军", "军队":"乌克兰陆军部队编号11316部队,乌克兰陆军部队编号11316部队", "武器": "", "伤亡": ""}

"2023年6月3日20时10分，乌克兰防空部队编号1136部队，在哈尔科夫市布朗尼镇检测到导弹袭击，立即分析上报。", {"时间":"2023年6月3日20时10分", "地点":"哈尔科夫市布朗尼镇", "人物": "", "军队":"乌克兰防空部队编号1136部队", "武器": "", "伤亡": ""}

"还有消息称，清水河多个据点已被同盟军占领，禁止通行。", {"时间": "", "地点":"清水河", "人物": "", "军队": "同盟军", "武器": "", "伤亡": ""}

"据当地居民消息，今日凌晨4点开始，有武装团体同时袭击掸邦北部腊戌、登尼、贵概、达莫尼、南非卡、木姐、南坎、瑟兰、滚弄、货班、清水河、老街地军事部署区。", {"时间":"凌晨4点", "地点":"掸邦北部腊戌,登尼,贵概,达莫尼,南非卡,木姐,南坎,瑟兰,滚弄,货班,清水河,老街", "人物": "", "军队": "", "武器": "", "伤亡": ""}

"据确切消息，从10月27日凌晨4点开始，以上多个地区军事部署区、收费站、警察哨所、所有的警察局均同时受到相关武装力量攻击。", {"时间":"10月27日凌晨4点", "地点": "军事部署区,收费站,警察哨所,警察局", "人物": "", "军队": "", "武器": "", "伤亡": ""}

"据央视军事消息，据缅甸媒体报道，10月27日，缅北腊戌、贵慨等多地的缅军军事据点遭武装袭击并爆发交火，战事激烈。", {"时间":"10月27日", "地点":"缅北腊戌,缅北贵慨", "人物": "", "军队": "", "武器": "", "伤亡": ""}

"据中国侨网消息，据称，果敢民族民主同盟军发布公告对此次武装袭击负责，称行动旨在打击老街的电诈民团，因此从即日起封锁腊戌至清水河、木姐的道路。", {"时间": "", "地点":"腊戌,清水河,木姐", "人物": "", "军队": "果敢民族民主同盟军", "武器": "", "伤亡": ""}

"指挥中心派遣陆军第三保障部队前往。", {"时间":"", "地点":"", "人物": "", "军队":"陆军第三保障部队", "武器": "", "伤亡":""}

### Instruction: 

"""
    _t2 = """
以json格式( {"时间":"", "地点":"", "人物": "", "军队":"", "武器":"", "伤亡":""} )输出；如果某个实体里包含多项信息，请将它们用'，'隔开。

### Response:

"""
    jinja2_template = _t1 + "请分析\"{{_sentence}}\"" + _t2
    prompt = PromptTemplate.from_template(jinja2_template, template_format="jinja2")
    # prompt.format(_sentence="2023年6月3日20时10分，乌克兰防空预警检测外籍导弹入境，乌克兰军事指挥中心依据《军事入侵防御紧急方案》（乌-防空10586号），对该事件做出紧急应对措施，导弹途径基辅市、哈尔科夫市、奥德赛市、最终20时35分在顿涅茨克市发生爆炸，造成两座大楼炸毁，约160名平民伤亡，出动乌克兰防空1军和防空13军，共计10辆防空导弹装甲车，50枚防空导弹，150名士兵，对袭击时间做出紧急处理。")
    # print(prompt)



def tag_sentence(_sentence):
    if _sentence:
        
        return
    else:
        return "Error: sentence is empty!"

def text_tagging(_txt):
    _txt = clean_txt(_txt)
    txt_lines = _txt.split('\n')
    _sentences = []
    for i in txt_lines:
        i_li = i.strip()
        if i_li:
            for j in i_li.split("。"):
                if j:
                    jj = j+"。"
                    _sentences.append(jj)
    _JQ = []
    _log = []
    for i in range(0, len(_sentences)):
        i_re = tag_sentence(_sentences[i])
        _JQ.append(i_re)
        _log.append(f"'{_sentences[i]}'\n> {i_re}")        
    _JQ_str = ""
    if len(_sentences) == len(_JQ):
        _JQ_str = str(_JQ)
    else:
        _log = "Error: len(sentences) != len(JQ)" + "\n"
    return _JQ_str, "\n\n".join(_log)

def parse_txt(_txt):
    if _txt:
        _log = ""
        _JQ_str, _log = text_tagging(_txt)
        output_JQ_file = f"_JQ.txt"
        with open(output_JQ_file, "w", encoding='utf-8') as wf:
            wf.write(_JQ_str)
        return _log
    else:
        return ["错误: TXT不能为空！"]

def parse_file(file):
    if file:
        _log = ""
        if os.path.exists(file.name):
            with open(file.name, encoding='utf-8') as rf:
                _txt = rf.read()
            _JQ_str, _log = text_tagging(_txt)
            left, right = os.path.splitext(os.path.basename(file.name))
            global output_JQ_file
            output_JQ_file = f"{left}_JQ.txt"
            with open(output_JQ_file, "w", encoding='utf-8') as wf:
                wf.write(_JQ_str)
        return _log
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


##### UI
_description = """
# 应急事件 / 报文问答 / 命令解析 / 标签提取
"""
chat_ask = gr.Textbox(label="", placeholder="...", lines=5, max_lines=5, interactive=True, visible=True, scale=9)

with gr.Blocks(title=_description) as demo:
    dh_history = gr.State([])
    dh_user_question = gr.State("")
    gr.Markdown(_description)

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

