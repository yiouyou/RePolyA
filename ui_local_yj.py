import gradio as gr
import time

from repolya._const import LOG_ROOT
from repolya._log import logger_yj

from repolya.autogen.wf_jd import (
    generate_search_dict_for_event,
    generate_event_context,
    generate_event_plan,
)

_log_ans_yj_context = LOG_ROOT / '_ans_yj_context.txt'
_log_ans_yj_plan = LOG_ROOT / '_ans_yj_plan.txt'
_log_ref_yj = LOG_ROOT / '_ref_yj.txt'


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
    _dict = generate_search_dict_for_event(_event)
    global _content_fp
    _context, _content_fp = generate_event_context(_event, _dict)
    write_log_ans(_log_ans_yj_context, _context, 'done')
    #####
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"'梳理脉络'耗时：{execution_time:.1f} seconds"
    logger_yj.info(_time)
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
    logger_yj.info(_time)


def show_YJ_context(text):
    # print(f"text: {text}")
    if text:
        if _content_fp:
            return gr.File(value=_content_fp, visible=True)
    else:
        if _content_fp:
            return gr.File(value=_content_fp)

