import os
import re
import time
import shutil
import concurrent.futures as cf
import gradio as gr

from repolya.rag.vdb_faiss import (
    get_faiss_HuggingFace,
    merge_faiss_HuggingFace,
)
from repolya.rag.qa_chain import (
    qa_vdb_multi_query_textgen,
    qa_with_context_as_mio,
)
# from repolya.autogen.workflow import (
#     create_rag_task_list_zh,
#     search_faiss_openai,
# )
from repolya.rag.digest_dir import (
    calculate_md5,
    dir_to_faiss_HuggingFace,
)
from repolya.rag.doc_loader import clean_txt
from repolya.toolset.tool_bshr import bshr_vdb

from repolya._const import LOG_ROOT, WORKSPACE_RAG
from repolya._log import logger_rag


_upload_dir = WORKSPACE_RAG / 'lj_rag_upload'
_db_name = str(WORKSPACE_RAG / 'lj_rag_hf')
_clean_txt_dir = str(WORKSPACE_RAG / 'lj_rag_clean_txt')
if not os.path.exists(_upload_dir):
    os.makedirs(_upload_dir)
if not os.path.exists(_db_name):
    os.makedirs(_db_name)
if not os.path.exists(_clean_txt_dir):
    os.makedirs(_clean_txt_dir)


_log_ans_fast = LOG_ROOT / '_ans_fast.txt'
_log_ref_fast = LOG_ROOT / '_ref_fast.txt'
_log_ans_autogen = LOG_ROOT / '_ans_autogen.txt'
_log_ref_autogen = LOG_ROOT / '_ref_autogen.txt'


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


def rag_read_logs():
    with open(_log_ans_fast, "r") as f:
        _ans_fast = f.read()
    with open(_log_ref_fast, "r") as f:
        _ref_fast = f.read()
    with open(_log_ans_autogen, "r") as f:
        _ans_autogen = f.read()
    with open(_log_ref_autogen, "r") as f:
        _ref_autogen = f.read()
    return [_ans_fast, _ref_fast, _ans_autogen, _ref_autogen]


def rag_clean_logs():
    write_log_ans(_log_ans_fast,'')
    write_log_ref(_log_ref_fast,'')
    write_log_ans(_log_ans_autogen,'')
    write_log_ref(_log_ref_autogen,'')


rag_clean_logs()


def rag_clean_all():
    rag_clean_logs()
    print('rag_clean_logs()')
    return [gr.Textbox(value=""), gr.Button(variant="secondary")]


##### RAG
def rag_handle_upload(_tmp_path):
    _tmp_files = []
    _out = []
    for i in _tmp_path:
        i_fp = i.name
        _tmp_files.append(i_fp)
        i_fn = os.path.basename(i_fp)
        i_dir = os.path.dirname(i_fp)
        # print(i_dir)
        i_md5 = calculate_md5(i_fp)
        # print(i_md5)
        i_fn_new = f"{i_md5}" + os.path.splitext(os.path.basename(i_fp))[1]
        i_fp_new = os.path.join(_upload_dir, i_fn_new)
        i_db_name = os.path.join(_upload_dir, f"{i_md5}_hf")
        # print(i_fp_new)
        if not os.path.exists(i_fp_new):
            logger_rag.info(f"upload {i_fn} to {i_fn_new}")
            dir_to_faiss_HuggingFace(i_dir, i_db_name, _clean_txt_dir)
            shutil.move(i_fp, i_fp_new)
            merge_faiss_HuggingFace(_db_name, i_db_name)
            shutil.rmtree(i_db_name)
            logger_rag.info(f"done upload process")
            _out.append(f"upload {i_fn} to {i_fn_new}")
        else:
            logger_rag.info(f"{i_fn} ({i_fn_new}) exists")
            _out.append(f"{i_fn} ({i_fn_new}) exists")
    return "\n".join(_out)


def qa_faiss_HuggingFace(_query, _vdb):
    start_time = time.time()
    _textgen_url = "http://127.0.0.1:5552"
    _ans, _step, _token_cost = qa_vdb_multi_query_textgen(_query, _vdb, 'stuff', _textgen_url)
    end_time = time.time()
    execution_time = end_time - start_time
    _time = f"Time: {execution_time:.1f} seconds"
    logger_rag.info(f"{_time}")
    return [_ans, _step, _token_cost, _time]


def rag_helper_fast(_query):
    _vdb = get_faiss_HuggingFace(_db_name)
    _ans, _ref = "", ""
    write_log_ans(_log_ans_fast,'')
    write_log_ref(_log_ref_fast,'')
    with cf.ProcessPoolExecutor() as executor:
        write_log_ans(_log_ans_fast, '', 'continue')
        _ans, _step, _token_cost, _time = qa_faiss_HuggingFace(_query, _vdb)
        _ref = f"{_token_cost}\n{_time}\n\n{_step}"
        write_log_ans(_log_ans_fast, clean_txt(_ans), 'done')
        write_log_ref(_log_ref_fast, _ref)
    return


def rag_helper_autogen(_query):
    _vdb = get_faiss_HuggingFace(_db_name)
    _ans, _ref = "", ""
    # write_log_ans(_log_ans_autogen,'')
    # write_log_ref(_log_ref_autogen,'')
    # start_time = time.time()
    # write_log_ans(_log_ans_autogen, '', 'continue')
    # # ChatCompletion.start_logging(reset_counter=True, compact=False)
    # ### task list
    # _task_list, _token_cost = create_rag_task_list_zh(_query)
    # write_log_ans(_log_ans_autogen, f"生成的子问题列表：\n\n{_task_list}", 'continue')
    # end_time = time.time()
    # execution_time = end_time - start_time
    # _time = f"Time: {execution_time:.1f} seconds"
    # write_log_ref(_log_ref_autogen, f"\n\n{_time}")
    # # print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")
    # ### context
    # _context, _token_cost = search_faiss_openai(_task_list, _vdb)
    # write_log_ans(_log_ans_autogen, f"生成的 QA 上下文：\n\n{_context}", 'continue')
    # end_time = time.time()
    # execution_time = end_time - start_time
    # _time = f"Time: {execution_time:.1f} seconds"
    # write_log_ref(_log_ref_autogen, f"\n\n{_time}")
    # ### qa
    # _qa, _tc = qa_with_context_as_mio(_query, _context)
    # write_log_ans(_log_ans_autogen, f"生成的最终答案：\n\n{_qa}", 'done')
    # end_time = time.time()
    # execution_time = end_time - start_time
    # _time = f"Time: {execution_time:.1f} seconds"
    # write_log_ref(_log_ref_autogen, f"\n\n{_time}\n\n{'='*40}\n\n{_context}")
    return


def rag_helper(_query, _radio):
    if _radio == "快速":
        logger_rag.info("[快速]")
        rag_helper_fast(_query)
    if _radio == "多智":
        logger_rag.info("[多智]")
        rag_helper_autogen(_query)

