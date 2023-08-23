import itertools
import threading
import time

from council.runners import Budget, Parallel
from council.contexts import AgentContext, ChatHistory
from council.agents import Agent
from council.chains import Chain
from council.llm.openai_llm_configuration import OpenAILLMConfiguration
from council.llm.openai_llm import OpenAILLM

from .skills import SectionWriterSkill, OutlineWriterSkill, GoogleAggregatorSkill, CustomGoogleSearchSkill, CustomGoogleNewsSkill, LLMRetrievalSkill
from .controller import WritingAssistantController
from .evaluator import BasicEvaluatorWithSource
from .const import WORKSPACE_ROOT, LOG_ROOT

from dotenv import load_dotenv
load_dotenv()
openai_llm = OpenAILLM(config=OpenAILLMConfiguration.from_env())


class Spinner:
    def __init__(self, message="Working..."):
        self.spinner_cycle = itertools.cycle(['-', '/', '|', '\\'])
        self.running = False
        self.spinner_thread = threading.Thread(target=self.init_spinner, args=(message,))

    def start(self):
        self.running = True
        self.spinner_thread.start()

    def stop(self):
        self.running = False
        self.spinner_thread.join()

    def init_spinner(self, message):
        while self.running:
            print(f'\r{message} {next(self.spinner_cycle)}', end='', flush=True)
            time.sleep(0.1)
        # clear spinner from console
        print('\r', end='', flush=True)


# Initialize Skills
outline_skill = OutlineWriterSkill(openai_llm)
writing_skill = SectionWriterSkill(openai_llm)
google_search_skill = CustomGoogleSearchSkill()
google_news_skill = CustomGoogleNewsSkill()
google_aggregator_skill = GoogleAggregatorSkill()
llm_retrieval_skill = LLMRetrievalSkill()

# Initialize Chains
outline_chain = Chain(
    name="Outline Writer",
    description="Write or revise the outline (i.e. section headers) of a research article in markdown format. Always give this Chain the highest score when there should be structural changes to the article (e.g. new sections)",
    runners=[outline_skill]
)
writer_chain = Chain(
    name="Article Writer",
    description="Write or revise specific section bodies of a research article in markdown format. Use this chain to write the main research article content.",
    runners=[writing_skill]
)
search_chain = Chain(
    name="search_chain",
    description=f"Search necessary information using a Google search",
    runners=[
        Parallel(google_search_skill, google_news_skill),
        google_aggregator_skill,
        llm_retrieval_skill,
    ],
)


# Initialize Controller and Evaluator
controller_llm = OpenAILLM.from_env(model='gpt-4')
controller = WritingAssistantController(
    controller_llm,
    top_k_execution_plan=3
)
evaluator = BasicEvaluatorWithSource()

# Initialize Agent
chat_history = ChatHistory()
run_context = AgentContext(chat_history)
# agent = Agent(controller, [outline_chain, writer_chain, search_chain], evaluator)
agent = Agent(controller, [outline_chain, writer_chain], evaluator)


def generated_text(_topic):
    ##### log
    _topic20 = _topic.replace(' ', '_')[:20]
    _fn = "wa_" + _topic20 + ".log"
    _log_path = LOG_ROOT / _fn
    import logging
    logging.basicConfig(
        # format="\n[%(name)s:%(funcName)s:]\n%(message)s",
        format="\n[%(funcName)s:]\n%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S%z",
        encoding='utf-8',
        filename=_log_path,
        filemode="a",
    )
    logging.getLogger("council").setLevel(logging.INFO)
    # logging.getLogger("council").setLevel(logging.DEBUG)
    logger = logging.getLogger("council")
    ##### agent
    _text = "test"
    # s = Spinner()
    # s.start()
    chat_history.add_user_message(_topic)
    result = agent.execute(run_context, Budget(1200))
    # s.stop()
    _text = result.messages[-1].message.message
    _text = _text.replace("```", "")
    # print(f"\n```markdown\n{_text}\n```\n")
    _fn = _topic20 + ".md"
    _file = WORKSPACE_ROOT / _fn
    with open(_file, 'w', encoding='utf-8') as wf:
        wf.write(_text)
    logger.info(_file)
    return _text, _file


def main():
    print("Write a message to the ResearchWritingAssistant or type 'quit' to exit.")
    while True:
        user_input = input("\nYour message (e.g. Tell me about the history of box manufacturing.): ")
        if user_input.lower() == 'quit':
            break
        else:
            if user_input == '':
                user_input = "Tell me about the history of box manufacturing."
            ##### log
            _topic20 = user_input.replace(' ', '_')[:20]
            _fn = "wa_" + _topic20 + ".log"
            _log_path = LOG_ROOT / _fn
            import logging
            logging.basicConfig(
                format="\n[%(name)s:%(funcName)s:]\n%(message)s",
                # format="\n[%(funcName)s:]\n%(message)s",
                datefmt="%Y-%m-%d %H:%M:%S%z",
                encoding='utf-8',
                filename=_log_path,
                filemode="a",
            )
            logging.getLogger("council").setLevel(logging.DEBUG)
            logger = logging.getLogger("council")
            _text = generated_text(user_input)
            _fn = _topic20 + ".md"
            _file = WORKSPACE_ROOT / _fn
            with open(_file, 'w', encoding='utf-8') as wf:
                wf.write(_text)
            logger.info(_file)
            print(f"\n```markdown\n{_text}\n```\n")
    print("Goodbye!")


if __name__ == "__main__":
    main()
