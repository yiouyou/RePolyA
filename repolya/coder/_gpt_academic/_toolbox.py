import re
from repolya._const import WORKSPACE_ROOT
from repolya._log import logger_coder


def trimmed_format_exc():
    import os, traceback
    str = traceback.format_exc()
    current_path = os.getcwd()
    replace_path = "."
    return str.replace(current_path, replace_path)


def gen_time_str():
    import time
    return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())


def write_results_to_file(project_folder, history, file_name=None):
    """
    将对话记录history以Markdown格式写入文件中。如果没有指定文件名，则使用当前时间生成文件名。
    """
    logger_coder.debug(history)
    import os
    if file_name is None:
        file_name = 'Code_Digest_' + gen_time_str() + '.md'
    _fp = WORKSPACE_ROOT / file_name
    with open(_fp, 'w', encoding='utf8') as f:
        f.write('# Code Digest Report\n')
        f.write(f"## '{os.path.basename(project_folder)}'工程代码分析\n")
        for i, content in enumerate(history):
            try:    
                if type(content) != str: content = str(content)
            except:
                continue
            if i % 2 == 0:
                f.write('### ')
            try:
                f.write(content)
            except:
                # remove everything that cannot be handled by utf8
                f.write(content.encode('utf-8', 'ignore').decode())
            f.write('\n\n')
    wfn = os.path.abspath(_fp)
    res = '以上材料已经被写入:\t' + wfn
    logger_coder.info(f"{res}")
    print(wfn)
    return res, wfn


def get_reduce_token_percent(text):
    """
        * 此函数未来将被弃用
    """
    try:
        # text = "maximum context length is 4097 tokens. However, your messages resulted in 4870 tokens"
        pattern = r"(\d+)\s+tokens\b"
        match = re.findall(pattern, text)
        EXCEED_ALLO = 500  # 稍微留一点余地，否则在回复时会因余量太少出问题
        max_limit = float(match[0]) - EXCEED_ALLO
        current_tokens = float(match[1])
        ratio = max_limit/current_tokens
        assert ratio > 0 and ratio < 1
        return ratio, str(int(current_tokens-max_limit))
    except:
        return 0.5, '不详'

