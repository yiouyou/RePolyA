from pathlib import Path


def get_project_root():
    """逐级向上寻找项目根目录"""
    current_path = Path.cwd()
    while True:
        if (current_path / '.git').exists() or \
           (current_path / '.project_root').exists() or \
           (current_path / '.gitignore').exists():
            return current_path
        parent_path = current_path.parent
        if parent_path == current_path:
            raise Exception("Project root not found.")
        current_path = parent_path


PROJECT_ROOT = get_project_root() / 'repolya'
LOG_ROOT = PROJECT_ROOT / '_log'


##### autogen
WORKSPACE_AUTOGEN = PROJECT_ROOT / '_workspace' / '_autogen'
LOG_AUTOGEN = LOG_ROOT / 'autogen.log'
###
AUTOGEN_CONFIG = PROJECT_ROOT / 'autogen' / 'OAI_CONFIG_LIST'
AUTOGEN_DOC = WORKSPACE_AUTOGEN / 'doc'
AUTOGEN_REF = WORKSPACE_AUTOGEN / 'ref'
AUTOGEN_IMG = WORKSPACE_AUTOGEN / 'img'


##### azure
WORKSPACE_AZURE = PROJECT_ROOT / '_workspace' / '_azure'
LOG_AZURE = LOG_ROOT / 'azure.log'
###
AZURE_PROMPT = PROJECT_ROOT / 'azure' / '_prompt'


##### chat
WORKSPACE_CHAT = PROJECT_ROOT / '_workspace' / '_chat'
LOG_CHAT = LOG_ROOT / 'chat.log'


##### coder
WORKSPACE_CODER = PROJECT_ROOT / '_workspace' / '_coder'
LOG_CODER = LOG_ROOT / 'coder.log'
###
DEFAULT_WORKER_NUM = 1
TIMEOUT_SECONDS = 30
MAX_RETRY = 2
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"


##### metagpt
WORKSPACE_METAGPT = PROJECT_ROOT / '_workspace' / '_metagpt'
LOG_METAGPT = LOG_ROOT / 'metagpt.log'
###
TMP = PROJECT_ROOT / 'tmp'
DATA_PATH = PROJECT_ROOT / 'data'
WORKSPACE_ROOT = WORKSPACE_METAGPT
UT_PATH = PROJECT_ROOT / 'data' / 'ut'
UT_PY_PATH = PROJECT_ROOT / 'data' / 'ut' / 'files' / 'ut'
SWAGGER_PATH = PROJECT_ROOT / 'data' / 'ut' / 'files' / 'api'
API_QUESTIONS_PATH = PROJECT_ROOT / 'data' / 'ut' / 'files' / 'question/'
RESEARCH_PATH = PROJECT_ROOT / 'data' / 'research'
PROMPT_PATH = PROJECT_ROOT / 'metagpt '/ 'prompts'
YAPI_URL = "http://yapi.deepwisdomai.com/"
MEM_TTL = 24 * 30 * 3600


##### paper
WORKSPACE_PAPER = PROJECT_ROOT / '_workspace' / '_paper'
LOG_PAPER = LOG_ROOT / 'paper.log'
###
PAPER_PDF = WORKSPACE_PAPER / '_pdf'
PAPER_DIGEST = WORKSPACE_PAPER / '_pdf_digest'
PAPER_JSONL = WORKSPACE_PAPER / '_jsonl'
PAPER_SERVER_DUMP = PROJECT_ROOT / '_server_dump'
PAPER_PROMPT = PROJECT_ROOT / 'paper' / '_prompt'
PAPER_QLIST = PROJECT_ROOT / 'paper' / '_digest'


##### rag
WORKSPACE_RAG = PROJECT_ROOT / '_workspace' / '_rag'
LOG_RAG = LOG_ROOT / 'rag.log'
###
RAG_PDF = WORKSPACE_RAG / 'pdf'


##### toolset
WORKSPACE_TOOLSET = PROJECT_ROOT / '_workspace' / '_toolset'
LOG_TOOLSET = LOG_ROOT / 'toolset.log'


##### writer
WORKSPACE_WRITER = PROJECT_ROOT / '_workspace' / '_writer'
LOG_WRITER = LOG_ROOT / 'writer.log'

