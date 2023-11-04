from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from repolya.autogen.tool_function import (
    _def_save_output,
    save_output,
)

from autogen import (
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json,
)


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))


is_termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()
# lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")
# lambda x: True if "TERMINATE" in x.get("content") else False


# Base Configuration
base_config = {
    "config_list": config_list,
    "request_timeout": 300,
    "temperature": 0,
    "model": "gpt-3.5-turbo",
    "use_cache": False,
    # "seed": 42,
}


def is_termination_msg(content):
    have_content = content.get("content", None) is not None
    if have_content and "APPROVED" in content["content"]:
        return True
    return False

COMPLETION_PROMPT = "If everything looks good, respond with 'APPROVED'."


##### JDML - Organizer
USER_PROMPT_ZH = "作为'军事指挥'，你向'军事策划'提出问题并分配任务。"
JDML_task_user_zh = UserProxyAgent(
    name="JDML_task_用户",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=is_termination_msg,
    system_message=USER_PROMPT_ZH,
)


PLANNER_PROMPT_ZH = """作为'军事策划'，你将使用综合战场实时信息，为'军事指挥'提供军事决策、命令下达、作战监控功能，实现优化决策流程，获取最优作战方案，保障作战质量的目标。你需要将面临的复杂问题或任务分解为更具体可操作的子任务（不超过3个）。你将子任务列表发送给'军事参谋'进行核查，并根据'军事参谋'的反馈调整子任务列表，保持子任务数量在5个左右。如果'军事参谋'没有具体的改进建议，则保持输出不变。
每次输出时，都完整输出且只输出各子任务的目标和行动，格式示例如下：

阿拉伯数字编号）某个子任务标题
- 目标：...
- 行动：...

不用解释和注释，没有其他。
你将使用'save_output'函数将子任务列表保存到本地。
不要使用'save_output'函数保存'军事参谋'的反馈。
"""
JDML_task_planner_zh = AssistantAgent(
    name="JDML_task_规划师",
    code_execution_config=False,
    is_termination_msg=is_termination_msg,
    llm_config={
        **base_config,
        "functions": [_def_save_output],
    },
    function_map={
        'save_output': save_output,
    },
    system_message=PLANNER_PROMPT_ZH,
)


CRITIC_PROMPT_ZH = "作为'军事参谋'，你将仔细考查'军事策划'提供的子任务列表，并针对其不足，尽可能提出更优的具体的改进意见。"
JDML_task_critic_zh = AssistantAgent(
    name="JDML_task_评判者",
    is_termination_msg=is_termination_msg,
    llm_config={
        **base_config,
        "functions": [_def_save_output],
    },
    function_map={
        'save_output': save_output,
    },
    system_message=CRITIC_PROMPT_ZH,
)

