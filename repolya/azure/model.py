from repolya._const import WORKSPACE_AZURE
from repolya._log import logger_azure

import re
import os
import sys
from time import sleep
from tqdm import trange

from repolya.azure.chains.chains import Chains
from repolya.azure.chains.task_chains import TaskChains
from repolya.azure.utils import getCodeSnippet, init


def pretty_task_list(_task_list):
    _str = []
    for i in _task_list:
        _str.append(f"{i['step']}. {i['description']}\n - {i['task_name']} ({i['task_type']})\n - input: {i['input_key']} ({i['input_data_type']})\n - output: {i['output_key']} ({i['output_data_type']})")
    return "\n".join(_str)


class DemoGPT:
    def __init__(
        self,
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        model_name="gpt-3.5-turbo-0613",
        max_steps=10,
        openai_api_base="",
    ):
        assert len(
            openai_api_key.strip()
        ), "Either give openai_api_key as an argument or put it in the environment variable"
        self.model_name = model_name
        self.openai_api_key = openai_api_key
        self.max_steps = max_steps  # max iteration for refining the model purpose
        self.openai_api_base = openai_api_base
        Chains.setLlm(
            self.model_name, self.openai_api_key, openai_api_base=self.openai_api_base
        )
        TaskChains.setLlm(
            self.model_name, self.openai_api_key, openai_api_base=self.openai_api_base
        )

    def setModel(self, model_name):
        self.model_name = model_name
        Chains.setLlm(
            self.model_name, self.openai_api_key, openai_api_base=self.openai_api_base
        )
        TaskChains.setLlm(
            self.model_name, self.openai_api_key, openai_api_base=self.openai_api_base
        )

    def __repr__(self) -> str:
        return f"DemoGPT(model_name='{self.model_name}',max_steps={self.max_steps})"

    def __call__(
        self,
        instruction="Create a translation system that converts English to French",
        title="",
    ):
        _token_cost = []

        yield {
            "stage": "system_inputs",
            "completed": False,
            "percentage": 0,
            "done": False,
            "message": "System inputs are being detected...",
        }

        system_inputs, system_inputs_token_cost = Chains.systemInputs(instruction=instruction)
        logger_azure.debug(f"\nsystem_inputs:\n>>> {instruction}\n<<< '{system_inputs}'\n{system_inputs_token_cost}")
        _token_cost.append(system_inputs_token_cost)

        yield {
            "stage": "plan",
            "completed": False,
            "percentage": 10,
            "done": False,
            "message": "Plan creation has started...",
        }

        plan, plan_token_cost = Chains.planWithInputs(instruction=instruction, system_inputs=system_inputs)
        logger_azure.debug(f"\nplan:\n>>> {instruction}\n>>> {system_inputs}\n<<< '{plan}'\n{plan_token_cost}")
        _token_cost.append(plan_token_cost)

        yield {
            "stage": "plan",
            "completed": True,
            "percentage": 20,
            "done": False,
            "message": "Plan has been generated.",
        }

        sleep(1)

        yield {
            "stage": "task",
            "completed": False,
            "percentage": 30,
            "done": False,
            "message": "Task generation has started...",
        }

        task_list, task_list_token_cost = Chains.tasks(instruction=instruction, plan=plan)
        logger_azure.debug(f"\ntask_list:\n>>> {instruction}\n>>> {plan}\n<<< '{pretty_task_list(task_list)}'\n{task_list_token_cost}")
        _token_cost.append(task_list_token_cost)

        yield {
            "stage": "task",
            "completed": True,
            "percentage": 50,
            "done": False,
            "message": "Tasks have been generated.",
            "tasks": task_list,
        }

        sleep(1)

        yield {
            "stage": "task",
            "completed": True,
            "percentage": 55,
            "done": False,
            "message": "Tasks are being controlled.",
        }

        task_controller_result = Chains.taskController(tasks=task_list)
        logger_azure.debug(f"\ntask_controller_result:\n- feedback: {task_controller_result['feedback'].strip()}\n- valid: {task_controller_result['valid']}")

        for _ in range(self.max_steps):
            if not task_controller_result["valid"]:
                task_list, task_list_token_cost = Chains.refineTasks(
                    instruction=instruction,
                    tasks=task_list,
                    feedback=task_controller_result["feedback"],
                )
                logger_azure.debug(f"\nrefined_task_list:\n>>> {instruction}\n>>> {task_list}\n>>> {task_controller_result['feedback']}\n<<< '{pretty_task_list(task_list)}'\n{task_list_token_cost}")
                _token_cost.append(task_list_token_cost)
                task_controller_result = Chains.taskController(tasks=task_list)
                logger_azure.debug(f"\ntask_controller_result:\n- feedback: {task_controller_result['feedback'].strip()}\n- valid: {task_controller_result['valid']}")
            else:
                break

        code_snippets = init(title)
        logger_azure.debug(f"\ncode_snippets:\n```{code_snippets}```")

        sleep(1)

        yield {
            "stage": "draft",
            "completed": False,
            "percentage": 60,
            "done": False,
            "message": "Converting tasks to code snippets...",
        }

        num_of_tasks = len(task_list)
        logger_azure.debug(f"\nnum_of_tasks: {num_of_tasks}")

        for i, task in enumerate(task_list):
            code, code_token_cost = getCodeSnippet(task, code_snippets, self.max_steps)
            code = "### " + task["description"] + "\n" + code
            code_snippets += code
            yield {
                "stage": "draft",
                "completed": i + 1 == num_of_tasks,
                "percentage": 60 + int(20 * (i + 1) / num_of_tasks),
                "done": False,
                "message": f"{i+1}/{num_of_tasks} tasks have been converted to code",
                "code": code,
            }
            logger_azure.debug(f"{i+1}/{num_of_tasks} tasks have been converted to code\n<<< ```{code}```\n{code_token_cost}")
            _token_cost.extend(code_token_cost)

        sleep(1)

        yield {
            "stage": "draft",
            "completed": False,
            "percentage": 85,
            "done": False,
            "message": "Code snippets are being combined...",
        }
        
        final_code, final_code_token_cost = Chains.combine_v2(code_snippets=code_snippets)
        logger_azure.debug(f"\nfinal_code:\n>>> ```{code_snippets}```\n <<< ```{final_code}```\n{final_code_token_cost}")
        _token_cost.append(final_code_token_cost)

        _token_cost_str = "\n".join(_token_cost)
        logger_azure.debug(f"All Token Cost:\n'{_token_cost_str}'")
        logger_azure.info("Total " + extract_and_sum(_token_cost_str))

        yield {
            "stage": "final",
            "completed": True,
            "percentage": 100,
            "done": True,
            "message": "Final code has been generated.",
            "code": final_code,
        }


##### extract_and_sum
def extract_and_sum(text):
    # 用于存储总和
    total_tokens = 0
    total_prompt = 0
    total_completion = 0
    total_cost = 0.0
    # 使用正则表达式找出所有符合格式的行
    matches = re.findall(r"Tokens: (\d+) = \(Prompt (\d+) \+ Completion (\d+)\) Cost: \$(\d+.\d+)", text)
    # 遍历所有匹配项并加总
    for match in matches:
        # print(match)
        tokens, prompt, completion = map(int, match[:-1])
        cost = float(match[-1])
        total_tokens += tokens
        total_prompt += prompt
        total_completion += completion
        total_cost += cost
    # 整合结果
    _res = f"Tokens: {total_tokens} = (Prompt {total_prompt} + Completion {total_completion}) Cost: ${total_cost:.3f}"
    return _res

