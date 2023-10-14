from repolya.autogen.as_planner import PLANNER_user, PLANNER_planner

import os
import json
import requests
from bs4 import BeautifulSoup

from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate


_def_search = {
    "name": "search",
    "description": "google search for relevant information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Google search query",
            }
        },
        "required": ["query"],
    },
}
def search(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        'q': query
    })
    headers = {
        'X-API-KEY': 'e66757b85a72a921ca77f03cd1ac4489a3adb3a0',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


_def_scrape = {
    "name": "scrape",
    "description": "scraping website content based on url",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "website url to scrape",
            }
        },
        "required": ["url"],
    },
            }
def scrape(url: str):
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    data = {
        'url': url
    }
    data_json = json.dumps(data)
    response = requests.post(
        "https://chrome.browserless.io/content?token=0177d884-49c4-499c-bb13-a0dc0ab399bb",
        data=data_json,
        headers=headers
    )
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        print(f"web: {text}")
        if len(text) > 8000:
            output = summary(text)
            return output
        else:
          return text
    else:
        print(f"HTTP request failed with status code {response.status_code}")


def summary(content):
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"],
        chunk_size=5000,
        chunk_overlap=500
    )
    docs = text_splitter.create_documents([content])
    map_prompt = """
    Write a detailed summary of the following text for a research purpose:
    "{text}"
    SUMMARY:
    """
    map_prompt_template = PromptTemplate(
        template=map_prompt,
        input_variables=["text"]
    )
    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        map_prompt=map_prompt_template,
        verbose=True
    )
    output = summary_chain.run(input_documents=docs,)
    return output


_def_planner = {
    "name": "planner",
    "description": "ask planner to: 1. get a plan for finishing a task, 2. verify the execution result of the plan and potentially suggest new plan.",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "question to ask planner. Make sure the question include enough context, such as the code and the execution result. The planner does not know the conversation between you and the user, unless you share the conversation with the planner.",
            },
        },
        "required": ["message"],
    },
}
def planner(message):
    PLANNER_user.initiate_chat(
        PLANNER_planner,
        message=message
    )
    return PLANNER_user.last_message()["content"]


rd_functions = [_def_search, _def_scrape]
plantask_functions = [_def_planner]
