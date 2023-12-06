import gradio as gr
import time

from repolya._const import LOG_ROOT
from repolya._log import logger_jd

from repolya.autogen.wf_jd import (
    generate_search_dict_for_event,
    generate_event_context,
    generate_event_context_textgen,
    generate_event_plan,
)

_log_ans_yj_context = LOG_ROOT / '_ans_yj_context.txt'
_log_ans_yj_plan = LOG_ROOT / '_ans_yj_plan.txt'
_log_ref_yj = LOG_ROOT / '_ref_jd.txt'


yj_keyword = {
    "基本情况_1": "发生发展时间线",
    "基本情况_2": "灾害规模和强度",
    "处置过程_1": "实施应急响应和救援措施的时间线",
    "处置过程_2": "政府和非政府组织角色",#
    "军民协作_1": "军队参与救灾行动的时间线",
    "军民协作_2": "军队救援行动和协作细节",
    "法规依据_1": "军队协助救灾的法律依据",
    "法规依据_2": "应急救援军地联动机制",
    "影响评估_1": "灾害对经济和社会的影响",
    "影响评估_2": "受灾群体和地区的恢复进程",
    "反思启示_1": "灾害管理和应对的有效性评估",
    "反思启示_2": "灾害的经验教训和改进措施",
}

yj_section = [
    "基本情况",
    "处置过程",
    "军民协作",
    "法规依据",
    "影响评估",
    "反思启示",
]


def write_log_ans(_log_ans, _txt, _status=None):
    with open(_log_ans, 'w', encoding='utf-8') as wf:
        if _status == "continue":
            _txt += "\n\n计算中，预计需要30分钟，请稍候..."
        # elif _status == "done":
        #     _txt += "\n\n[完成]"
        wf.write(_txt)


def write_log_ref(_log_ref, _txt):
    with open(_log_ref, 'w', encoding='utf-8') as wf:
        wf.write(_txt)


def yj_read_logs():
    with open(_log_ref_yj, "r") as f:
        _ref_yj = f.read()
    with open(_log_ans_yj_context, "r") as f:
        _ans_yj_context = f.read()
    with open(_log_ans_yj_plan, "r") as f:
        _ans_yj_plan = f.read()
    return [_ref_yj, _ans_yj_context, _ans_yj_plan]


def yj_clean_logs():
    write_log_ref(_log_ref_yj,'')
    write_log_ans(_log_ans_yj_context,'')
    write_log_ans(_log_ans_yj_plan,'')


yj_clean_logs()


def yj_clean_all():
    yj_clean_logs()
    print('yj_clean_logs()')
    return [
        gr.Textbox(value=""), # yj_query
        gr.Button(variant="secondary"), # yj_start_btn
        gr.Button(variant="secondary"), # yj_plan_btn
        gr.Textbox(value=""), # yj_log
        gr.Textbox(value=""), # yj_context
        gr.Textbox(value=""), # yj_plan
    ]


##### yj
def yj_sort_out_context(_event):
    write_log_ans(_log_ans_yj_context, '')
    start_time = time.time()
    write_log_ans(_log_ans_yj_context, '', 'continue')
    #####
    _dict = generate_search_dict_for_event(_event, yj_keyword)
    global _content_fp
    _context, _content_fp = generate_event_context(_event, _dict, yj_keyword, yj_section)
    write_log_ans(_log_ans_yj_context, _context, 'done')
    #####
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"'梳理脉络'耗时：{execution_time:.1f} seconds"
    logger_jd.info(_time)
    time.sleep(1)
    return gr.Button(variant="primary")


def yj_sort_out_context_textgen(_event):
    write_log_ans(_log_ans_yj_context, '')
    start_time = time.time()
    write_log_ans(_log_ans_yj_context, '', 'continue')
    #####
    _dict = generate_search_dict_for_event(_event, yj_keyword)
    global _content_fp
    _content_fp = ""
    _textgen_url = "http://127.0.0.1:5552"
    _context, _content_fp = generate_event_context_textgen(_event, _dict, _textgen_url, yj_keyword, yj_section)
    # _context, _content_fp = generate_event_context(_event, _dict, yj_keyword, yj_section)
    write_log_ans(_log_ans_yj_context, _context, 'done')
    #####
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"'梳理脉络'耗时：{execution_time:.1f} seconds"
    logger_jd.info(_time)
    time.sleep(1)
    return gr.Button(variant="primary")


def yj_write_plan(_event, _context):
    write_log_ans(_log_ans_yj_plan, '')
    start_time = time.time()
    write_log_ans(_log_ans_yj_plan, '', 'continue')
    #####
    _plan = generate_event_plan(_event, _context)
    write_log_ans(_log_ans_yj_plan, _plan, 'done')
    #####
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"'总结报告'耗时：{execution_time:.1f} seconds"
    logger_jd.info(_time)


def show_yj_context(text):
    # print(f"text: {text}")
    if text:
        if _content_fp:
            return gr.File(value=_content_fp, visible=True)
    else:
        if _content_fp:
            return gr.File(value=_content_fp)

