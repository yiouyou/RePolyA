from council.skills import SkillBase, LLMSkill, PromptToMessages
from council.skills.google import GoogleSearchSkill, GoogleNewsSkill
from council.contexts import ChatMessage, ChainContext, SkillContext
from council.runners import Budget
from council.prompt import PromptBuilder
from council.llm import LLMBase, LLMMessage, OpenAILLM
from typing import List

from .prompt import _prompt


class OutlineWriterSkill(SkillBase):
    """Write or revise the outline of an article."""
    def __init__(self, llm: LLMBase):
        """Build a new OutlineWriterSkill."""
        super().__init__(name="OutlineWriterSkill")
        self.llm = llm
        self.system_prompt = _prompt['skill']['outlinewriter']['sys']
        self.main_prompt_template = _prompt['skill']['outlinewriter']['human']

    def execute(self, context: ChainContext, _budget: Budget) -> ChatMessage:
        """Execute `OutlineWriterSkill`."""
        # Get the chat message history
        chat_message_history = [
            f"{m.kind}: {m.message}" for m in context.messages
        ]
        # Get the article
        article = context.last_message.data['article']
        # Get the outline
        outline = context.last_message.data['outline']
        # Get the iteration
        iteration = context.last_message.data['iteration']
        # Get the instructions
        instructions = context.last_message.message
        main_prompt = self.main_prompt_template.substitute(
            conversation_history=chat_message_history,
            article=article,
            article_outline=outline,
            instructions=instructions
        )
        messages_to_llm = [
            LLMMessage.system_message(self.system_prompt),
            LLMMessage.assistant_message(
                main_prompt
            ),
        ]
        llm_result = self.llm.post_chat_request(messages=messages_to_llm, temperature=0.1)
        llm_response = llm_result.first_choice
        return ChatMessage.skill(
            source=self.name,
            message="I've edited the outline and placed the response in the 'data' field.",
            data={'outline': llm_response, 'instructions': instructions, 'iteration': iteration},
        )
    

class SectionWriterSkill(SkillBase):
    """Write a specific section of an article."""
    def __init__(self, llm: LLMBase):
        """Build a new SectionWriterSkill."""
        super().__init__(name="SectionWriterSkill")
        self.llm = llm
        self.system_prompt = _prompt['skill']['sectionwriter']['sys']
        self.main_prompt_template = _prompt['skill']['sectionwriter']['human']

    def execute(self, context: ChainContext, _budget: Budget) -> ChatMessage:
        """Execute `SectionWriterSkill`."""
        # Get the chat message history
        conversation_history = [
            f"{m.kind}: {m.message}" for m in context.messages
        ]
        # Get the article
        article = context.last_message.data['article']
        # Get the outline
        outline = context.last_message.data['outline']
        # Get the iteration
        iteration = context.last_message.data['iteration']
        # Get the instructions
        instructions = context.last_message.message
        main_prompt = self.main_prompt_template.substitute(
            conversation_history=conversation_history,
            outline=outline,
            article=article,
            instructions=instructions
        )
        messages_to_llm = [
            LLMMessage.system_message(self.system_prompt),
            LLMMessage.assistant_message(
                main_prompt
            ),
        ]
        llm_result = self.llm.post_chat_request(messages=messages_to_llm, temperature=0.1)
        llm_response = llm_result.first_choice
        return ChatMessage.skill(
            source=self.name,
            message="I've written or edited the article and placed it in the 'data' field.",
            data={'article': llm_response, 'instructions': instructions, 'iteration': iteration},
        )


class CustomGoogleSearchSkill(GoogleSearchSkill):
    """
    A skill that performs a Google search using the reformulated query from the controller.
    Based on GoogleSearchSkill: https://github.com/chain-ml/council/blob/main/council/skills/google/google_search_skill.py
    """
    def execute(self, context: SkillContext, budget: Budget) -> ChatMessage:
        # Execute the skill only if the API keys required for Google Search are provided
        if self.gs:
            prompt = context.current.messages[-1]
            resp = self.gs.execute(query=prompt.message, nb_results=5)
            response_count = len(resp)
            if response_count > 0:
                return self.build_success_message(
                    f"{self._name} {response_count} responses for {prompt.message}", json.dumps([r.dict() for r in resp])
                )
            return self.build_error_message("no response")
        return self.build_error_message("API keys for Google Search not provided")


class CustomGoogleNewsSkill(GoogleNewsSkill):
    """
    A skill that performs a Google News search using the reformulated query from the controller.
    Based on GoogleNewsSkill: https://github.com/chain-ml/council/blob/main/council/skills/google/google_news_skill.py
    """
    def execute(self, context: SkillContext, budget: Budget) -> ChatMessage:
        prompt = context.current.messages[-1]
        resp = self.gn.execute(query=prompt.message, nb_results=5)
        response_count = len(resp)
        if response_count > 0:
            return self.build_success_message(
                f"gnews {response_count} responses for {prompt.message}", json.dumps([r.dict() for r in resp])
            )
        return self.build_error_message("no response")


class GoogleAggregatorSkill(SkillBase):
    """Skill to aggregate results from Google Search and Google News"""
    def __init__(
        self,
    ):
        super().__init__(name="google_aggregator")

    def execute(self, context: SkillContext, budget: Budget) -> ChatMessage:
        gsearch_results = (
            json.loads(context.current.last_message_from_skill("gsearch").data)
            if context.current.last_message_from_skill("gsearch").is_ok
            else []
        )
        gnews_results = (
            json.loads(context.current.last_message_from_skill("gnews").data)
            if context.current.last_message_from_skill("gnews").is_ok
            else []
        )
        search_results = gsearch_results + gnews_results
        context = ""
        for result in search_results:
            text = result.get("title", "") + " " + result.get("snippet", "") + "\n\n"
            context += text
        return self.build_success_message(context)


class LLMRetrievalSkill:
    def __new__(cls):
        # Initialize with the default prompt dictionary        
        def build_context_messages(context: 'SkillContext') -> List['LLMMessage']:
            """Context messages function for LLMSkill."""
            context_message_prompt = PromptToMessages(prompt_builder=PromptBuilder(_prompt['skill']['llmretrieval']['human']))
            return context_message_prompt.to_user_message(context)
        # Return an instance of LLMSkill
        return LLMSkill(
            llm=OpenAILLM.from_env(model='gpt-3.5-turbo-16k'),
            system_prompt=_prompt['skill']['llmretrieval']['sys'],
            context_messages=build_context_messages,
        )

