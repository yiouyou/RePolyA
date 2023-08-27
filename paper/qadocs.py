#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from paperqa import Docs

# llm_stream = ChatOpenAI(model='gpt-4', callbacks=[StreamingStdOutCallbackHandler()], streaming=True)
llm = ChatOpenAI(model='gpt-4')
llm_summary = ChatOpenAI(model='gpt-3.5-turbo')

docs = Docs(llm=llm, summary_llm=llm_summary)

def qadocs(_query, _pathlist):
    for _file in _pathlist:
        try:
            if _file.lower().endswith('.pdf') or _file.lower().endswith('.txt'):
                docs.add(_file, chunk_chars=500)
                print(_file)
        except ValueError as e:
            print('Could not read', _file, e)
    _ans = docs.query(_query)
    ##### formatted_answer, question/answer/references, context
    return _ans


if __name__ == "__main__":
    from const import PDF_ROOT
    _list = []
    import os
    _dir = PDF_ROOT
    # print(_dir)
    _files = os.listdir(_dir)
    for _fn in _files:
        _fp = os.path.join(_dir, _fn)
        if os.path.isfile(_fp):
            # print(f"File: {_fn}")
            _list.append(_fp)
        # elif os.path.isdir(_fp):
        #     print(f"Folder: {_fn}")
    print(_list)
    _query = "What manufacturing challenges are unique to bispecific antibodies?"
    _ans = qadocs(_query, _list)
    print('-'*40)
    print(_ans.formatted_answer)
    print('-'*40)
    print(_ans.question)
    print('-'*40)
    print(_ans.answer)
    print('-'*40)
    print(_ans.references)
    print('-'*40)
    print(_ans.context)
    print('-'*40)
else:
    from .const import PDF_ROOT
