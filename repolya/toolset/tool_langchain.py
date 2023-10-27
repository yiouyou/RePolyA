from langchain.utilities import BingSearchAPIWrapper
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.utilities import OpenWeatherMapAPIWrapper
from langchain.utilities import SerpAPIWrapper
from langchain.utilities import WikipediaAPIWrapper
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper

from langchain.tools import StructuredTool
from langchain.tools import DuckDuckGoSearchRun
from langchain.tools import DuckDuckGoSearchResults
from langchain.tools import GooglePlacesTool
from langchain.tools import HumanInputRun
from langchain.tools import PubmedQueryRun
from langchain.tools import ShellTool
from langchain.tools import WikipediaQueryRun
from langchain.tools import YouTubeSearchTool
from langchain.tools.yahoo_finance_news import YahooFinanceNewsTool

from langchain.tools.file_management import (
    ReadFileTool,
    CopyFileTool,
    DeleteFileTool,
    MoveFileTool,
    WriteFileTool,
    ListDirectoryTool,
)
from langchain.agents.agent_toolkits import FileManagementToolkit
from langchain.agents import Tool

from tempfile import TemporaryDirectory

import os


##### get_all_tool_names()
# ['python_repl',
#  'requests',
#  'requests_get',
#  'requests_post',
#  'requests_patch',
#  'requests_put',
#  'requests_delete',
#  'terminal',
#  'sleep',
#  'wolfram-alpha',
#  'google-search',
#  'google-search-results-json',
#  'searx-search-results-json',
#  'bing-search',
#  'metaphor-search',
#  'ddg-search',
#  'google-serper',
#  'google-serper-results-json',
#  'searchapi',
#  'searchapi-results-json',
#  'serpapi',
#  'dalle-image-generator',
#  'twilio',
#  'searx-search',
#  'wikipedia',
#  'arxiv',
#  'golden-query',
#  'pubmed',
#  'human',
#  'awslambda',
#  'sceneXplain',
#  'graphql',
#  'openweathermap-api',
#  'dataforseo-api-search',
#  'dataforseo-api-search-json',
#  'eleven_labs_text2speech',
#  'news-api',
#  'tmdb-api',
#  'podcast-api',
#  'llm-math',
#  'open-meteo-api']

# search_ddg = DuckDuckGoSearchRun()
# search_ddg_more = DuckDuckGoSearchResults()

# search_bing = BingSearchAPIWrapper()
# search_goolge = GoogleSearchAPIWrapper()
# # search_google_serper = GoogleSerperAPIWrapper()
# # search_serp = SerpAPIWrapper()

# wolfram_alpha = WolframAlphaAPIWrapper()
# shell_tool = ShellTool()

# wiki_query = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
# pubmed_query = PubmedQueryRun()

# weather_map = OpenWeatherMapAPIWrapper()
# google_places = GooglePlacesTool()


##### FileManagementToolkit:
# 'copy_file'
# 'file_delete'
# 'file_search'
# 'move_file'
# 'read_file'
# 'write_file'
# 'list_directory'
### If you don't provide a root_dir, operations will default to the current working directory
working_directory = TemporaryDirectory()
file_tools = FileManagementToolkit(
    root_dir=str(working_directory.name),
    selected_tools=[
        "copy_file",
        "file_delete",
        "file_search",
        "move_file",
        "read_file",
        "write_file",
        "list_directory"
    ],
).get_tools()

# ##### human
# def get_input() -> str:
#     print("Insert your text. Enter 'q' or press Ctrl-D (or Ctrl-Z on Windows) to end.")
#     contents = []
#     while True:
#         try:
#             line = input()
#         except EOFError:
#             break
#         if line == "q":
#             break
#         contents.append(line)
#     return "\n".join(contents)
# human_input = HumanInputRun(input_func=get_input)


##### custom
from langchain.tools.base import ToolException
def _handle_error(error: ToolException) -> str:
    return (
        "The following errors occurred during tool execution:"
        + error.args[0]
        + "Please try another tool."
    )

yfinance_news = YahooFinanceNewsTool()
youtube_search = YouTubeSearchTool()
search_ddg_news = DuckDuckGoSearchResults(api_wrapper=DuckDuckGoSearchAPIWrapper(region="zh-CN", time="d", max_results=3), backend="news")

search_yfinance_news = Tool.from_function(
    func=yfinance_news,
    name="search_yfinance_news",
    description="useful for when you need to search news from yahoo finance",
    handle_tool_error=_handle_error,
)
search_youtube = Tool.from_function(
    func=youtube_search,
    name="search_youtube",
    description="useful for when you need to search videos/audios from youtube",
    handle_tool_error=_handle_error,
)
search_ddg_news = Tool.from_function(
    func=search_ddg_news,
    name="search_ddg_news",
    description="useful for when you need to search news with duckduckgo",
    handle_tool_error=_handle_error,
)



# def multiplier(a, b):
#     return a * b
# def parsing_multiplier(string):
#     a, b = string.split(",")
#     return multiplier(int(a), int(b))
# llm = OpenAI(temperature=0)
# tools = [
#     Tool(
#         name="Multiplier",
#         func=parsing_multiplier,
#         description="useful for when you need to multiply two numbers together. The input to this tool should be a comma separated list of numbers of length two, representing the two numbers you want to multiply together. For example, `1,2` would be the input if you wanted to multiply 1 by 2.",
#     )
# ]
# mrkl = initialize_agent(
#     tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
# )
# mrkl.run("What is 3 times 4")



# def post_message(url: str, body: dict, parameters: Optional[dict] = None) -> str:
#     """Sends a POST request to the given url with the given body and parameters."""
#     result = requests.post(url, json=body, params=parameters)
#     return f"Status: {result.status_code} - {result.text}"
# tool = StructuredTool.from_function(post_message)



# @tool("search", return_direct=True)
# def search_api(query: str) -> str:
#     """Searches the API for the query."""
#     return "Results"

# @tool
# def post_message(url: str, body: dict, parameters: Optional[dict] = None) -> str:
#     """Sends a POST request to the given url with the given body and parameters."""
#     result = requests.post(url, json=body, params=parameters)
#     return f"Status: {result.status_code} - {result.text}"

