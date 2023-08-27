from council.contexts import AgentContext, ScoredChatMessage, ChatMessage, ChatMessageKind
from council.chains import Chain
from council.llm import LLMMessage, LLMBase
from council.utils import Option
from council.runners import Budget
from council.controllers import ControllerBase, ExecutionUnit

from typing import List, Tuple

from repolya.writer.prompt import _prompt
from repolya._log import logger_writer


class WritingAssistantController(ControllerBase):
    """
    A controller that uses an LLM to decide the execution plan
    """
    def __init__(
        self,
        llm: LLMBase,
        response_threshold: float = 0,
        top_k_execution_plan: int = 5,
    ):
        """
        Initialize a new instance
        Parameters:
            llm (LLMBase): the instance of LLM to use
            response_threshold (float): a minimum threshold to select a response from its score
            top_k_execution_plan (int): maximum number of execution plan returned
        """
        self._llm = llm
        self._response_threshold = response_threshold
        self._top_k = top_k_execution_plan
        # Controller state variables 
        self._article = ""
        self._outline = ""
        self._iteration = 0

    def get_plan(
        self, context: AgentContext, chains: List[Chain], budget: Budget
    ) -> List[ExecutionUnit]:
        """
        Planning phase.
        """
        system_prompt = _prompt['controller']['get_plan']['sys']
        main_prompt_template = _prompt['controller']['get_plan']['human']
        # Increment iteration
        self._iteration += 1
        # Get the Chain details
        chain_details = "\n ".join(
            [f"name: {c.name}, description: {c.description}" for c in chains]
        )
        # Get the conversation history
        conversation_history = [f"{m.kind}: {m.message}" for m in context.chatHistory.messages]
        messages = [
            LLMMessage.system_message(system_prompt),
            LLMMessage.user_message(
                main_prompt_template.substitute(
                    chains=chain_details,
                    outline=self._outline,
                    article=self._article,
                    conversation_history=conversation_history,
                )
            ),
        ]
        llm_result = self._llm.post_chat_request(messages=messages)
        response = llm_result.first_choice
        logger_writer.debug(f"controller get_plan response: {response}")
        parsed = response.splitlines()
        parsed = [p for p in parsed if len(p) > 0]
        parsed = [self.parse_line(line, chains) for line in parsed]
        filtered = [
            r.unwrap()
            for r in parsed
            if r.is_some() and r.unwrap()[1] > self._response_threshold
        ]
        if (filtered is None) or (len(filtered) == 0):
            return []
        filtered.sort(key=lambda item: item[1], reverse=True)
        result = []
        for chain, score, instruction in filtered: 
            initial_state = ChatMessage.chain(
                message=instruction, data={"article": self._article, "outline": self._outline, "iteration": self._iteration}
            )
            exec_unit = ExecutionUnit(
                chain,
                budget,
                initial_state=initial_state,
                name=f"{chain.name}: {instruction}"
            )
            result.append(exec_unit)
        result = result[: self._top_k]
        return result

    @staticmethod
    def parse_line(line: str, chains: List[Chain]) -> Option[Tuple[Chain, int, str]]:
        result: Option[Tuple[Chain, int, str]] = Option.none()
        try:
            (name, score, instruction) = line.split(";")[:3]
            chain = next(filter(lambda item: item.name == name, chains))
            result = Option.some((chain, int(score), instruction))
        except Exception as e:
            logger_writer.error(f"Controller parsing error: {e}.\n{line}")
        finally:
            return result
        
    def select_responses(self, context: AgentContext) -> List[ScoredChatMessage]:
        """
        Aggregation phase. 
        Get latest iteration results from Evaluator and aggregate if applicable.
        """
        all_eval_results = sorted(context.evaluationHistory[-1], key=lambda x: x.score, reverse=True)
        current_iteration_results = []
        for scored_result in all_eval_results:
            message = scored_result.message
            logger_writer.debug(f"message: {message}")
            if message.data['iteration'] == self._iteration:
                current_iteration_results.append(message)
        ## If multiple outlines or articles were generated in the last iteration, 
        ## use LLM calls to aggregate them.
        outlines = []
        articles = []
        conversation_history = [f"{m.kind}: {m.message}" for m in context.chatHistory.messages]
        for message in current_iteration_results:
            source = message.source
            if source == "SectionWriterSkill":
                articles.append(message.data['article'])
            elif source == "OutlineWriterSkill":
                outlines.append(message.data['outline'])
        ##### Outline Aggregation
        system_prompt = _prompt['controller']['select_responses']['aggregate_outline']['sys']
        main_prompt_template = _prompt['controller']['select_responses']['aggregate_outline']['human']
        if len(outlines) > 0:
            messages = [
                LLMMessage.system_message(system_prompt),
                LLMMessage.user_message(
                    main_prompt_template.substitute(
                        conversation_history=conversation_history,
                        existing_outline=self._outline,
                        possible_outlines=outlines
                    )
                ),
            ]
            llm_result = self._llm.post_chat_request(messages=messages)
            response = llm_result.first_choice
            self._outline = response
        ##### Article Aggregation
        system_prompt = _prompt['controller']['select_responses']['aggregate_article']['sys']
        main_prompt_template = _prompt['controller']['select_responses']['aggregate_article']['human']
        if len(articles) > 0:
            messages = [
                LLMMessage.system_message(system_prompt),
                LLMMessage.user_message(
                    main_prompt_template.substitute(
                        conversation_history=conversation_history,
                        article_outline=self._outline,
                        existing_article=self._article,
                        partial_articles = articles
                    )
                ),
            ]
            llm_result = self._llm.post_chat_request(messages=messages)
            self._article = llm_result.first_choice
        ##### Decide whether to keep iterating or to return the article to the user for review.
        system_prompt = _prompt['controller']['select_responses']['whether_edit']['sys']
        main_prompt_template = _prompt['controller']['select_responses']['whether_edit']['human']
        messages = [
            LLMMessage.system_message(system_prompt),
            LLMMessage.user_message(
                main_prompt_template.substitute(
                    article=self._article,
                    outline=self._outline,
                    conversation_history=conversation_history,
                )
            ),
        ]
        llm_result = self._llm.post_chat_request(messages=messages)
        response = llm_result.first_choice
        logger_writer.debug(f"outline: {self._outline}")
        logger_writer.debug(f"article: {self._article}")
        logger_writer.debug(f"controller editing decision: {response}")
        if "KEEP EDITING" in response:
            return []
        else:
            return [ScoredChatMessage(ChatMessage(message=self._article, kind=ChatMessageKind.Agent), 1.0)]

