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
WORKSPACE_CHAT = PROJECT_ROOT / '_workspace' / '_chat'
WORKSPACE_CODER = PROJECT_ROOT / '_workspace' / '_coder'
WORKSPACE_METAGPT = PROJECT_ROOT / '_workspace' / '_metagpt'
WORKSPACE_PAPER = PROJECT_ROOT / '_workspace' / '_paper'
WORKSPACE_WRITER = PROJECT_ROOT / '_workspace' / '_writer'
LOG_ROOT = PROJECT_ROOT / '_log'

### metagpt
TMP = PROJECT_ROOT / 'tmp'
DATA_PATH = PROJECT_ROOT / 'data'
WORKSPACE_ROOT = WORKSPACE_METAGPT
UT_PATH = PROJECT_ROOT / 'data' / 'ut'
UT_PY_PATH = PROJECT_ROOT / 'data' / 'ut' / 'files' / 'ut'
SWAGGER_PATH = PROJECT_ROOT / 'data' / 'ut' / 'files' / 'api'
API_QUESTIONS_PATH = PROJECT_ROOT / 'data' / 'ut' / 'files' / 'question/'
RESEARCH_PATH = PROJECT_ROOT / 'data' / "research"
PROMPT_PATH = PROJECT_ROOT / 'metagpt '/ 'prompts'
YAPI_URL = "http://yapi.deepwisdomai.com/"
MEM_TTL = 24 * 30 * 3600

### paper
JSONL_ROOT = WORKSPACE_PAPER / '_jsonl'
PDF_ROOT = WORKSPACE_PAPER / '_pdf'
SERVER_DUMP_ROOT = PROJECT_ROOT / '_server_dumps'

### writing

### coder
DEFAULT_WORKER_NUM = 1
TIMEOUT_SECONDS = 30
MAX_RETRY = 2
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"

