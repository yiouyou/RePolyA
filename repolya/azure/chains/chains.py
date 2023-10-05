import json
import os
import re

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)
from langchain.callbacks import get_openai_callback

from repolya.azure.controllers import checkDTypes
from repolya.azure.utils import refine

from . import prompts


class Chains:
    @classmethod
    def setLlm(
        cls,
        model,
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        temperature=0.0,
        openai_api_base=None,
    ):
        cls.llm = ChatOpenAI(
            model=model,
            openai_api_key=openai_api_key,
            temperature=temperature,
            openai_api_base=openai_api_base,
        )

    @classmethod
    def getChain(cls, system_template="", human_template="", **kwargs):
        prompts = []
        if system_template:
            prompts.append(SystemMessagePromptTemplate.from_template(system_template))
        if human_template:
            prompts.append(HumanMessagePromptTemplate.from_template(human_template))
        chat_prompt = ChatPromptTemplate.from_messages(prompts)
        with get_openai_callback() as cb:
            _res = LLMChain(llm=cls.llm, prompt=chat_prompt).run(**kwargs)
            _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
        return _res, _token_cost

    @classmethod
    def systemInputs(cls, instruction):
        return cls.getChain(
            system_template=prompts.system_inputs.system_template,
            human_template=prompts.system_inputs.human_template,
            instruction=instruction,
        )

    # @classmethod
    # def plan(cls, instruction):
    #     return cls.getChain(
    #         system_template=prompts.plan.system_template,
    #         human_template=prompts.plan.human_template,
    #         instruction=instruction,
    #     )

    @classmethod
    def planWithInputs(cls, instruction, system_inputs):
        plan, _token_cost = cls.getChain(
            system_template=prompts.plan_with_inputs.system_template,
            human_template=prompts.plan_with_inputs.human_template,
            instruction=instruction,
            system_inputs=system_inputs,
        )
        refined_plan = cls.refinePlan(plan)
        return refined_plan, _token_cost

    @classmethod
    def refinePlan(cls, plan):
        pattern = r'\[[a-zA-Z0-9_]+\(.*\)'
        steps = plan.strip().split("\n")
        refined_plan = []
        index = 1
        for i in range(len(steps)):
            step = steps[i]
            # If current step contains the pattern or next step contains the pattern, then retain
            if re.search(pattern, step):
                # Remove existing numbering
                current_step = re.sub(r'^\d+\.', "", step).strip()
                refined_plan.append(f"{index}. {current_step}")
                index += 1
        return "\n".join(refined_plan)
    
    @classmethod
    def tasks(cls, instruction, plan):
        task_list, _token_cost = cls.getChain(
            system_template=prompts.tasks.system_template,
            human_template=prompts.tasks.human_template,
            instruction=instruction,
            plan=plan,
        )
        return json.loads(task_list), _token_cost

    @classmethod
    def taskController(cls, tasks):
        return checkDTypes(tasks)

    @classmethod
    def refineTasks(cls, instruction, tasks, feedback):
        task_list, _token_cost = cls.getChain(
            system_template=prompts.task_refiner.system_template,
            human_template=prompts.task_refiner.human_template,
            instruction=instruction,
            tasks=tasks,
            feedback=feedback,
        )
        return json.loads(task_list), _token_cost

    # @classmethod
    # def combine(cls, instruction, code_snippets, plan):
    #     code, _token_cost = cls.getChain(
    #         system_template=prompts.combine.system_template,
    #         human_template=prompts.combine.human_template,
    #         instruction=instruction,
    #         code_snippets=code_snippets,
    #         plan=plan,
    #     )
    #     return refine(code), _token_cost

    @classmethod
    def combine_v2(cls, code_snippets):
        code, _token_cost = cls.getChain(
            system_template=prompts.combine_v2.system_template,
            human_template=prompts.combine_v2.human_template,
            code_snippets=code_snippets,
        )
        return refine(code), _token_cost

    # @classmethod
    # def refine(cls, instruction, code, feedback):
    #     code, _token_cost = cls.getChain(
    #         system_template=prompts.refine.system_template,
    #         human_template=prompts.refine.human_template,
    #         instruction=instruction,
    #         code=code,
    #         feedback=feedback,
    #     )
    #     return refine(code), _token_cost

    # @classmethod
    # def feedback(cls, instruction, code):
    #     return cls.getChain(
    #         system_template=prompts.feedback.system_template,
    #         human_template=prompts.feedback.human_template,
    #         instruction=instruction,
    #         code=code,
    #     )
        
    # @classmethod
    # def final(cls, draft_code):
    #     code, _token_cost = cls.getChain(
    #         system_template=prompts.final.system_template,
    #         human_template=prompts.final.human_template,
    #         draft_code=draft_code,
    #     )
    #     return refine(code), _token_cost
