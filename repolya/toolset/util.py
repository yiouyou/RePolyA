from langchain.document_loaders.merge import MergedDataLoader
from langchain.docstore.document import Document

from datetime import datetime, timedelta
from typing import List
import re


def parse_intermediate_steps(_list):
    _steps = []
    for n in range(len(_list)):
        i = _list[n]
        i_str = f"Step {n+1}: {i[0].tool}\n"
        i_str += f"> {i[0].tool_input}\n"
        i_str += f"< {i[0].log}\n"
        i_str += f"# {i[1]}\n"
        _steps.append(i_str)
    return "\n".join(_steps)


def merge_doc_loader(_list: List[Document]):
    loader_all = MergedDataLoader(loaders=_list)
    docs_all = loader_all.load()
    return docs_all


def calc_token_cost(_tc: list):
    total_tokens = 0
    total_prompt = 0
    total_completion = 0
    total_cost = 0.0
    # 对于列表中的每个字符串，使用正则表达式解析出需要的数字
    for entry in _tc:
        tokens_match = re.search(r"Tokens: (\d+)", entry)
        prompt_match = re.search(r"Prompt (\d+)", entry)
        completion_match = re.search(r"Completion (\d+)", entry)
        cost_match = re.search(r"Cost: \$([\d.]+)", entry)
        if tokens_match:
            total_tokens += int(tokens_match.group(1))
        if prompt_match:
            total_prompt += int(prompt_match.group(1))
        if completion_match:
            total_completion += int(completion_match.group(1))
        if cost_match:
            total_cost += float(cost_match.group(1))
    # 格式化并输出结果
    output = f"Tokens: {total_tokens} = (Prompt {total_prompt} + Completion {total_completion}) Cost: ${total_cost:.5f}"
    return output


def get_date(text):
    now = datetime.now()
    now_weekday = now.weekday()
    qt_pattern = r'^前(.+)天$'
    qt_match = re.search(qt_pattern, text)
    ht_pattern = r'^后(.+)天$'
    ht_match = re.search(ht_pattern, text)
    count = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '两': 2, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7}
    xz_pattern = r'^下周(.+)$'
    xz_match = re.search(xz_pattern, text)
    weekday = {'一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '七': 6, '日': 6, '天': 6 , '1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6}
    if '今天' in text or '当天' in text:
        return now.strftime('%Y-%m-%d')
    elif '昨天' in text:
        return (now - timedelta(1)).strftime('%Y-%m-%d')
    elif '明天' in text:
        return (now + timedelta(1)).strftime('%Y-%m-%d')
    elif '后天' in text:
        return (now + timedelta(2)).strftime('%Y-%m-%d')
    elif qt_match:
        day = count[qt_match.group(1)]
        return (now - timedelta(day)).strftime('%Y-%m-%d')
    elif ht_match:
        day = count[ht_match.group(1)]
        return (now + timedelta(day)).strftime('%Y-%m-%d')
    elif xz_match:
        day = weekday[xz_match.group(1)]
        return (now + timedelta(7 + day - now_weekday)).strftime('%Y-%m-%d')
    else:
        return f"error: {text}"
# print(get_date('下下周三'))

