import os
import json
import requests
from bs4 import BeautifulSoup

from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain import PromptTemplate

# import openai
# from dotenv import load_dotenv
# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")


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

