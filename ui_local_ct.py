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

_log_ans_ct_context = LOG_ROOT / '_ans_ct_context.txt'
_log_ans_ct_plan = LOG_ROOT / '_ans_ct_plan.txt'
_log_ref_ct = LOG_ROOT / '_ref_jd.txt'


ct_keyword = {
    "基本情况_1": "发生发展时间线",
    "基本情况_2": "冲突规模和强度",
    "影响评估_1": "冲突对国际政治的影响",
    "影响评估_2": "冲突对国际经济的影响",
}

ct_section = [
    "基本情况",
    "影响评估",
]


def write_log_ans(_log_ans, _txt, _status=None):
    with open(_log_ans, 'w', encoding='utf-8') as wf:
        if _status == "continue":
            _txt += "\n\n计算中，预计需要10分钟，请稍候..."
        # elif _status == "done":
        #     _txt += "\n\n[完成]"
        wf.write(_txt)


def write_log_ref(_log_ref, _txt):
    with open(_log_ref, 'w', encoding='utf-8') as wf:
        wf.write(_txt)


def ct_read_logs():
    with open(_log_ref_ct, "r") as f:
        _ref_ct = f.read()
    with open(_log_ans_ct_context, "r") as f:
        _ans_ct_context = f.read()
    with open(_log_ans_ct_plan, "r") as f:
        _ans_ct_plan = f.read()
    return [_ref_ct, _ans_ct_context, _ans_ct_plan]


def ct_clean_logs():
    write_log_ref(_log_ref_ct,'')
    write_log_ans(_log_ans_ct_context,'')
    write_log_ans(_log_ans_ct_plan,'')


ct_clean_logs()


def ct_clean_all():
    ct_clean_logs()
    print('ct_clean_logs()')
    return [
        gr.Textbox(value=""), # ct_query
        gr.Button(variant="secondary"), # ct_start_btn
        gr.Button(variant="secondary"), # ct_plan_btn
        gr.Textbox(value=""), # ct_log
        gr.Textbox(value=""), # ct_context
        gr.Textbox(value=""), # ct_plan
    ]


##### ct
def ct_sort_out_context(_event):
    write_log_ans(_log_ans_ct_context, '')
    start_time = time.time()
    write_log_ans(_log_ans_ct_context, '', 'continue')
    #####
    _dict = generate_search_dict_for_event(_event, ct_keyword)
    global _content_fp
    _context, _content_fp = generate_event_context(_event, _dict, ct_keyword, ct_section)
    write_log_ans(_log_ans_ct_context, _context, 'done')
    #####
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"'梳理脉络'耗时：{execution_time:.1f} seconds"
    logger_jd.info(_time)
    time.sleep(1)
    return gr.Button(variant="primary")


def ct_sort_out_context_textgen(_event):
    write_log_ans(_log_ans_ct_context, '')
    start_time = time.time()
    write_log_ans(_log_ans_ct_context, '', 'continue')
    #####
    _dict = generate_search_dict_for_event(_event, ct_keyword)
    global _content_fp
    _content_fp = ""
    _textgen_url = "http://127.0.0.1:5552"
    # _context, _content_fp = generate_event_context_textgen(_event, _dict, _textgen_url, ct_keyword, ct_section)
    _context, _content_fp = generate_event_context(_event, _dict, ct_keyword, ct_section)
    write_log_ans(_log_ans_ct_context, _context, 'done')
    #####
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"'梳理脉络'耗时：{execution_time:.1f} seconds"
    logger_jd.info(_time)
    time.sleep(1)
    return gr.Button(variant="primary")


def ct_write_plan(_event, _context):
    write_log_ans(_log_ans_ct_plan, '')
    start_time = time.time()
    write_log_ans(_log_ans_ct_plan, '', 'continue')
    #####
    _plan = generate_event_plan(_event, _context)
    write_log_ans(_log_ans_ct_plan, _plan, 'done')
    #####
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"'总结报告'耗时：{execution_time:.1f} seconds"
    logger_jd.info(_time)


def show_ct_context(text):
    # print(f"text: {text}")
    if text:
        if _content_fp:
            return gr.File(value=_content_fp, visible=True)
    else:
        if _content_fp:
            return gr.File(value=_content_fp)

