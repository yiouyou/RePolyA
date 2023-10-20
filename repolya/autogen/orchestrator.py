from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from typing import List, Optional, Tuple, Union
from autogen import (
    ConversableAgent,
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json,
)


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))

class Orchestractor:
    def __init__(
        self,
        name: Optional[str] = "Orchestractor",
        agents: List[ConversableAgent],
    ):
        self.name = name
        self.agents = agents
        self.messages = []
        self.completed_keyword = "APPROVED"
        self.error_keyword = "ERROR"
        if len(self.agents) < 2:
            raise Exception("Orchestractor needs at least 2 agents.")

    @property
    def total_agents(self):
        return len(self.agents)

    @property
    def last_message_is_dict(self):
        return isinstance(self.messages[-1], dict)

    @property
    def last_message_is_string(self):
        return isinstance(self.messages[-1], str)

    @property
    def last_message_is_func_call(self):
        return self.last_message_is_dict and self.latest_message.get(
            "function_call", None
        )

    @property
    def last_message_is_content(self):
        return self.last_message_is_dict and self.latest_message.get(
            "content", None
        )

    @property
    def latest_message(self) -> Union[str, dict]:
        if not self.messages:
            return None
        return self.messages[-1]

    def add_message(self, message: str):
        self.messages.append(message)

    def has_functions(self, agent: ConversableAgent):
        return agent._function_map is not None

    def basic_chat(
        self,
        agent_a: ConversableAgent,
        agent_b: ConversableAgent,
        message: str,
    ):
        print(f"basic_chat(): {agent_a.name} -> {agent_b.name}")
        agent_a.send(message, agent_b)
        reply = agent_b.generate_reply(sender=agent_a)
        self.add_message(reply)
        print(f"basic_chat(): replied with '{reply}'")

    def memory_chat(
        self,
        agent_a: ConversableAgent,
        agent_b: ConversableAgent,
        message: str,
    ):
        print(f"memory_chat(): {agent_a.name} -> {agent_b.name}")
        agent_a.send(message, agent_b)
        reply = agent_b.generate_reply(sender=agent_a)
        agent_b.send(reply, agent_b)
        self.add_message(reply)

    def function_chat(
        self,
        agent_a: ConversableAgent,
        agent_b: ConversableAgent,
        message: str,
    ):
        print(f"function_chat(): {agent_a.name} -> {agent_b.name}")
        self.basic_chat(agent_a, agent_a, message)
        assert self.last_message_is_content
        self.basic_chat(agent_a, agent_b, self.latest_message)

    def sequential_conversation(self, prompt: str) -> Tuple[bool, List[str]]:
        """ Runs a sequential conversation with the agents.
        For example:
            "Agent A" -> "Agent B" -> "Agent C" -> "Agent D" -> "Agent E"
        """
        print(f"\n---------- {self.name} Orchestrator Starting ----------\n")
        self.add_message(prompt)
        for idx, agent_iterate in enumerate(self.agents[:-1]):
            agent_a = self.agents[idx]
            agent_b = self.agents[idx + 1]
            print(f"\n---------- Running iterate {idx} with (agent_a: {agent_a.name}, agent_b: {agent_b.name}) ----------\n")
            # aget_a -> chat -> agent_b
            if self.last_message_is_string:
                self.basic_chat(agent_a, agent_b, self.latest_message)
            # agent_a -> func() -> agent_b
            if self.last_message_is_func_call and self.has_functions(agent_a):
                self.function_chat(agent_a, agent_b, self.latest_message)
            if idx == self.total_agents - 2:
                print(f"---------- Orchestrator Complete ----------\n")
                was_successful = self.completed_keyword in self.latest_message
                if was_successful:
                    print(f"✅ Orchestrator was successful")
                else:
                    print(f"❌ Orchestrator failed")
                return was_successful, self.messages

    def broadcast_conversation(self, prompt: str) -> Tuple[bool, List[str]]:
        """ Broadcast a message from agent_a to all agents.
        For example:
            "Agent A" -> "Agent B"
            "Agent A" -> "Agent C"
            "Agent A" -> "Agent D"
            "Agent A" -> "Agent E"
        """
        print(f"\n---------- {self.name} Orchestrator Starting ----------\n")
        self.add_message(prompt)
        broadcast_agent = self.agents[0]
        for idx, agent_iterate in enumerate(self.agents[1:]):
            print(f"\n---------- Running iterate {idx} with (agent_broadcast: {broadcast_agent.name}, agent_iteration: {agent_iterate.name}) ----------\n")
            # agent_a -> chat -> agent_b
            if self.last_message_is_string:
                self.memory_chat(broadcast_agent, agent_iterate, prompt)
            # agent_a -> func() -> agent_b
            if self.last_message_is_func_call and self.has_functions(agent_iterate):
                self.function_chat(agent_iterate, agent_iterate, self.latest_message)
        print(f"---------- Orchestrator Complete ----------\n")
        print(f"✅ Orchestrator was successful")
        return True, self.messages

