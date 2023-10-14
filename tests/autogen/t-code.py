import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.autogen.workflow import do_simple_code


_task='''For certain cloud services (such as computing), assuming there are several given attributes (such as vCore, memory, iops, storage, backup, etc.) of each computing resource sku, write a flexible and basic recommendation class to filter out unfitted skus and find the lowest price as the recommendation for customers.'''
re = do_simple_code(_task)
print(f"out: '{re}'")


# import os
# from dotenv import load_dotenv
# load_dotenv(os.path.join(_RePolyA, '.env'), override=True, verbose=True)

# from repolya._const import WORKSPACE_AUTOGEN, AUTOGEN_CONFIG
# from repolya._log import logger_autogen

# from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
# import autogen


# config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))
# llm_config = {
#     "config_list": config_list,
#     "seed":42,
#     "request_timeout":120
# }

# me = UserProxyAgent(
#     name="me",
#     code_execution_config={
#         "work_dir": WORKSPACE_AUTOGEN,
#         "last_n_messages": 2
#     },
#     system_message="A human admin who will give the idea and run the code provided by Coder.",
#     human_input_mode="ALWAYS",
# )

# coder = AssistantAgent(
#     name="coder",
#     llm_config=llm_config,
# )

# pm = AssistantAgent(
#     name="product_menager",
#     llm_config=llm_config,
#     system_message="You will help break down the initial idea into a well scoped requirement for the coder; Do not involve in future conversations or error fixing",
# )

# groupchat = autogen.GroupChat(
#     agents=[me, coder, pm],
#     messages=[]
# )

# manager = autogen.GroupChatManager(
#     name="RD",
#     groupchat=groupchat,
#     llm_config=llm_config
# )

# me.initiate_chat(
#     manager,
#     message="For certain cloud services (such as computing), assuming there are several given attributes (such as vCore, memory, iops, storage, backup, etc.) of each computing resource sku, write a flexible and basic recommendation class to filter out unfitted skus and find the lowest price as the recommendation for customers."
# )

