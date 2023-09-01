from repolya.coder._gpt_academic.crazy_functions.parse_source import parse_source_c
from repolya.coder._gpt_academic.crazy_functions.parse_source import parse_source_csharp
from repolya.coder._gpt_academic.crazy_functions.parse_source import parse_source_golang
from repolya.coder._gpt_academic.crazy_functions.parse_source import parse_source_java
from repolya.coder._gpt_academic.crazy_functions.parse_source import parse_source_js
from repolya.coder._gpt_academic.crazy_functions.parse_source import parse_source_python
from repolya.coder._gpt_academic.crazy_functions.parse_source import parse_source_rust
from repolya.coder._gpt_academic.crazy_functions.parse_source import parse_source_lua
from repolya._log import logger_coder

import os
from dotenv import load_dotenv
load_dotenv()


llm_kwargs = {
    'api_key': os.environ.get("OPENAI_API_KEY"),
    'llm_model': os.environ.get("OPENAI_LLM_MODEL"),
    "temperature": 0,
    "top_p": 1.0
}

def parsesource(_project_folder, _type):
    logger_coder.debug(_project_folder)
    _ans, _steps = "", ""
    if _type == 'c':
        parse_source_c(_project_folder, llm_kwargs, [])
    elif _type == 'csharp':
        parse_source_csharp(_project_folder, llm_kwargs, [])
    elif _type == 'golang':
        parse_source_golang(_project_folder, llm_kwargs, [])
    elif _type == 'java':
        parse_source_java(_project_folder, llm_kwargs, [])
    elif _type == 'js':
        parse_source_js(_project_folder, llm_kwargs, [])
    elif _type == 'python':
        parse_source_python(_project_folder, llm_kwargs, [])
    elif _type == 'rust':
        parse_source_rust(_project_folder, llm_kwargs, [])
    elif _type == 'lua':
        parse_source_lua(_project_folder, llm_kwargs, [])
    else:
        logger_coder.error(f"{_type}")
    return _ans, _steps

