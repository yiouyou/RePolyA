from langchain.tools import tool
from langchain.tools import StructuredTool

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.callbacks import get_openai_callback

from repolya._log import logger_toolset
from repolya.app.bshr.prompt import (
    SYS_BRAINSTORM,
    SYS_BRAINSTORM_ZH,
    SYS_HYPOTHESIS,
    SYS_HYPOTHESIS_ZH,
    SYS_SATISFICE,
    SYS_SATISFICE_ZH,
    SYS_REFINE,
    SYS_REFINE_ZH,
)

from halo import Halo
import requests
import json
import re


def bshr_chain(_sys: str, _text: str):
    _re, _token_cost = "", ""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _sys),
            ("human", "{text}"),
        ]
    )
    model = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0)
    runnable = (
        {"text": RunnablePassthrough()}
        | prompt 
        | model 
        | StrOutputParser()
    )
    with get_openai_callback() as cb:
        _re = runnable.invoke(_text)
        _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
    return _re, _token_cost


def search_wikipedia(query: str) -> (str, str):
    spinner = Halo(text='Information Foraging...', spinner='dots')
    spinner.start()
    url = 'https://en.wikipedia.org/w/api.php'
    search_params = {
        'action': 'query',
        'list': 'search',
        'srsearch': query,
        'format': 'json'
    }
    response = requests.get(url, params=search_params)
    data = response.json()
    title = data['query']['search'][0]['title']
    content_params = {
        'action': 'query',
        'prop': 'extracts',
        'exintro': True,
        'explaintext': True,
        'titles': title,
        'format': 'json'
    }
    response = requests.get(url, params=content_params)
    data = response.json()
    page_id = list(data['query']['pages'].keys())[0]
    content = data['query']['pages'][page_id]['extract']
    url = f"https://en.wikipedia.org/?curid={page_id}"
    spinner.stop()
    return content, url


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


def brainstorm(_query: str, _notes: str, _queries: str):
    _tc = []
    _sys = SYS_BRAINSTORM
    _spr = SYS_REFINE
    _human = f"""
# USER QUERY
{_query}


# NOTES
{_notes}


# PREVIOUS QUERIES
{_queries}
"""
    _re, _token_cost = bshr_chain(_sys, _human)
    _tc.append(_token_cost)
    logger_toolset.info(f"new questions: {_re}")
    _questions = json.loads(_re)
    for _q in _questions:
        content, url = search_wikipedia(_q)
        compressed_content, spr_tokens = bshr_chain(_spr, content)
        _tc.append(spr_tokens)
        _notes = f"{_notes}\n\nURL: {url}\nNOTE: {compressed_content}"
        logger_toolset.info(_q)
        logger_toolset.info(url)
        # logger_toolset.info(content)
        logger_toolset.info(compressed_content)
        _queries = f"""
{_queries}

QUESTION: {_q}

"""
    return _queries, _notes, calc_token_cost(_tc)


def hypothesize(_query: str, _notes: str, _hypotheses: str):
    _sys = SYS_HYPOTHESIS
    _human = f"""
# USER QUERY
{_query}


# NOTES
{_notes}


# PREVIOUS HYPOTHISES
{_hypotheses}
"""
    _re, _token_cost = bshr_chain(_sys, _human)
    # logger_toolset.info(f"new hypothesis: '{_re}'")
    return _re, _token_cost


def satisfice(_query: str, _notes: str, _queries: str, _hypothesis: str):
    _sys = SYS_SATISFICE
    _human = f"""# USER QUERY
{_query}


# NOTES
{_notes}


# QUERIES AND ANSWERS
{_queries}


# FINAL HYPOTHESIS
{_hypothesis}

"""
    _re, _token_cost = bshr_chain(_sys, _human)
    _feedback = json.loads(_re)
    return _feedback["satisficed"], _feedback["feedback"], _token_cost


def refine(_notes: str):
    _sys = SYS_REFINE
    _human = _notes
    _re, _token_cost = bshr_chain(_sys, _human)
    return _re, _token_cost


def run_bshr(_query: str):
    logger_toolset.info(f"query: '{_query}'")
    _tc = []
    notes = ""
    queries = ""
    iteration = 0
    max_iterations = 3
    hypotheses_feedback = "# FEEDBACK ON HYPOTHESES\n"
    while True:
        iteration += 1
        logger_toolset.info(f"iteration ({iteration}) started")
        new_queries, notes, _token_cost = brainstorm(
            _query=_query,
            _notes=notes, 
            _queries=queries,
        )
        queries += new_queries
        _tc.append(_token_cost)
        new_hypothesis, _token_cost = hypothesize(
            _query=_query,
            _notes=notes,
            _hypotheses=hypotheses_feedback,
        )
        _tc.append(_token_cost)
        satisficed, feedback, _token_cost = satisfice(
            _query=_query,
            _notes=notes,
            _queries=queries,
            _hypothesis=new_hypothesis,
        )
        _tc.append(_token_cost)
        hypotheses_feedback = f"""
{hypotheses_feedback}

## HYPOTHESIS
{new_hypothesis}

## FEEDBACK
{feedback}
"""
        logger_toolset.info(f"new_hypothesis: '{new_hypothesis}'")
        logger_toolset.info(f"satisficed: '{satisficed}'")
        logger_toolset.info(f"feedback: '{feedback}'")
        if satisficed or max_iterations <= iteration:
            logger_toolset.info(f"reached max iterations: {max_iterations <= iteration}")
            break
        notes, _token_cost = refine(notes)
        _tc.append(_token_cost)
        logger_toolset.info(f"iteration ({iteration}) completed")
    _re = new_hypothesis.split("\n")[-1]
    return _re, calc_token_cost(_tc)

