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

### metagpt
DATA_PATH = PROJECT_ROOT / 'data'
WORKSPACE_ROOT = PROJECT_ROOT / '_workspace'
PROMPT_PATH = PROJECT_ROOT / 'metagpt/prompts'
UT_PATH = PROJECT_ROOT / 'data/ut'
SWAGGER_PATH = UT_PATH / "files/api/"
UT_PY_PATH = UT_PATH / "files/ut/"
API_QUESTIONS_PATH = UT_PATH / "files/question/"
YAPI_URL = "http://yapi.deepwisdomai.com/"
TMP = PROJECT_ROOT / 'tmp'
RESEARCH_PATH = DATA_PATH / "research"
MEM_TTL = 24 * 30 * 3600

### paper
JSONL_ROOT = PROJECT_ROOT / '_workspace/_jsonl'
PDF_ROOT = PROJECT_ROOT / '_workspace/_pdf'
DUMP_ROOT = PROJECT_ROOT / '_server_dumps'

### writing
LOG_ROOT = PROJECT_ROOT / '_log'

### coder
DEFAULT_WORKER_NUM = 1
TIMEOUT_SECONDS = 30
MAX_RETRY = 2
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"

