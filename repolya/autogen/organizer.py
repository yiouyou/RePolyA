from repolya._const import AUTOGEN_CONFIG, WORKSPACE_AUTOGEN
from repolya._log import logger_autogen

from autogen import (
    ConversableAgent,
    config_list_from_json,
)

from typing import List, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
import tiktoken
import json
import time
import os


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))


@dataclass
class Chat:
    from_name: str
    to_name: str
    message: str
    created: int = field(default_factory=time.time)

@dataclass
class ConversationResult:
    success: bool
    messages: List[Chat]
    cost: float
    tokens: int
    last_message_str: str
    error_message: str


class AgentInstruments:
    """
    Base class for multi-agent instruments. Instruments are tools, state, and functions that an agent can use across the lifecycle of conversations
    """

    def __init__(self) -> None:
        self.session_id = None
        self.messages = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def sync_messages(self, messages: list):
        """
        Syncs messages with the organizer
        """
        raise NotImplementedError

    def make_agent_chat_file(self, team_name: str):
        return os.path.join(self.root_dir, f"agent_chats_{team_name}.json")

    def make_agent_cost_file(self, team_name: str):
        return os.path.join(self.root_dir, f"agent_cost_{team_name}.json")

    @property
    def root_dir(self):
        return os.path.join(str(WORKSPACE_AUTOGEN / "agent_results"), self.session_id)


class Organizer:
    """
    Orchestrators manage conversations between multi-agent teams.
    """

    def __init__(
        self,
        name: str,
        agents: List[ConversableAgent],
        agent_instruments: AgentInstruments,
        validate_results_func: callable = None,
    ):
        # Name of agent team
        self.name = name
        # List of agents
        self.agents = agents
        # List of raw messages - partially redundant due to self.chats
        self.messages = []
        # Agent instruments - state and functions that agents can use
        self.agent_instruments = agent_instruments
        # List of chats - {from, to, message}
        self.chats: List[Chat] = []
        # Function to validate results at the end of every conversation
        self.validate_results_func = validate_results_func
        if len(self.agents) < 2:
            raise Exception("Organizer needs at least two agents.")

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
    
    @property
    def last_message_always_string(self):
        if not self.messages:
            return ""
        if self.last_message_is_content:
            return self.latest_message.get("content", "")
        return str(self.messages[-1])

    def handle_validate_func(self) -> Tuple[bool, str]:
        """
        Run the validate_results_func if it exists
        """
        if self.validate_results_func:
            return self.validate_results_func()
        return True, ""

    def send_message(
        self,
        from_agent: ConversableAgent,
        to_agent: ConversableAgent,
        message: str
    ):
        """
        Send a message from one agent to another.
        Record the message in chat log in the orchestrator
        """
        from_agent.send(message, to_agent)
        self.chats.append(
            Chat(
                from_name=from_agent.name,
                to_name=to_agent.name,
                message=str(message),
            )
        )

    def add_message(self, message: str):
        """
        Add a message to the orchestrator
        """
        self.messages.append(message)

    def get_message_as_str(self):
        """
        Get all messages as a string
        """
        messages_as_str = ""
        for message in self.messages:
            if message is None:
                continue
            if isinstance(message, dict):
                content_from_dict = message.get("content", None)
                func_call_from_dict = message.get("function_call", None)
                content = content_from_dict or func_call_from_dict
                if not content:
                    continue
                messages_as_str += str(content)
            else:
                messages_as_str += str(message)
        return messages_as_str

    def get_cost_and_tokens(self):
        return estimate_price_and_tokens(self.get_message_as_str())

    def has_functions(self, agent: ConversableAgent):
        return len(agent._function_map) > 0

    def basic_chat(
        self,
        agent_a: ConversableAgent,
        agent_b: ConversableAgent,
        message: str,
    ):
        print(f"basic_chat(): {agent_a.name} -> {agent_b.name}")
        self.send_message(agent_a, agent_b, message)
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
        self.send_message(agent_a, agent_b, message)
        reply = agent_b.generate_reply(sender=agent_a)
        self.send_message(agent_b, agent_b, message)
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
    
    def self_function_chat(self, agent: ConversableAgent, message: str):
        print(f"self_function_chat(): {agent.name}")
        self.send_message(agent, agent, message)
        reply = agent.generate_reply(sender=agent)
        self.send_message(agent, agent, message)
        self.add_message(reply)
        print(f"self_function_chat(): replied with:", reply)
    
    def spy_on_agents(self, append_to_file: bool = True):
        conversations = []
        for chat in self.chats:
            conversations.append(asdict(chat))
        if append_to_file:
            file_name = self.agent_instruments.make_agent_chat_file(self.name)
            with open(file_name, "w", encoding='utf-8') as f:
                f.write(json.dumps(conversations, ensure_ascii=False, indent=4))

    def sequential_conversation(self, prompt: str) -> ConversationResult:
        """ Runs a sequential conversation with the agents.
        For example:
            "Agent A" -> "Agent B" -> "Agent C" -> "Agent D" -> "Agent E"
        """
        print(f"\n---------- {self.name} Organizer Starting (sequential_conversation) ----------\n")
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
            self.spy_on_agents()
            if idx == self.total_agents - 2:
                if self.has_functions(agent_b):
                    # agent_b -> func() -> agent_b
                    self.self_function_chat(agent_b, self.latest_message)
                print(f"---------- Organizer Complete (sequential_conversation) ----------\n")
                was_successful, error_message = self.handle_validate_func()
                self.spy_on_agents()
                if was_successful:
                    print(f"✅ sequential_conversation was successful")
                else:
                    print(f"❌ sequential_conversation failed")
                cost, tokens = self.get_cost_and_tokens()
                return ConversationResult(
                    success=was_successful,
                    messages=self.messages,
                    cost=cost,
                    tokens=tokens,
                    last_message_str=self.last_message_always_string,
                    error_message=error_message,
                )

    def broadcast_conversation(self, prompt: str) -> ConversationResult:
        """ Broadcast a message from agent_a to all agents.
        For example:
            "Agent A" -> "Agent B"
            "Agent A" -> "Agent C"
            "Agent A" -> "Agent D"
            "Agent A" -> "Agent E"
        """
        print(f"\n---------- {self.name} Organizer Starting (broadcast_conversation) ----------\n")
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
            self.spy_on_agents()
        print(f"---------- Organizer Complete (broadcast_conversation) ----------\n")
        was_successful, error_message = self.handle_validate_func()
        if was_successful:
            print(f"✅ broadcast_conversation was successful")
        else:
            print(f"❌ broadcast_conversation failed")
        cost, tokens = self.get_cost_and_tokens()
        return ConversationResult(
            success=was_successful,
            messages=self.messages,
            cost=cost,
            tokens=tokens,
            last_message_str=self.last_message_always_string,
            error_message=error_message,
        )

    def round_robin_conversation(
        self, prompt: str, loops: int = 1
    ) -> ConversationResult:
        """
        Runs a basic round robin conversation between agents:
        Example for a setup with agents A, B, and C:
            (1)
            A -> B
            B -> C
            C -> A
            (2)
            A -> B
            B -> C
            C -> A
            ...
        `loops` determines the number of times the sequence is repeated.
        """
        print(f"\n---------- {self.name} Organizer Starting (round_robin_conversation) ----------\n\n")
        self.add_message(prompt)
        total_iterations = loops * len(self.agents)
        for iteration in range(total_iterations):
            idx = iteration % len(self.agents)
            agent_a = self.agents[idx]
            agent_b = self.agents[(idx + 1) % len(self.agents)]
            print(
                f"\n\n💬 ---------- Running iteration {iteration} with conversation ({agent_a.name} -> {agent_b.name}) ----------\n\n",
            )
            # if we're back at the first agent, we need to reset the last message to the prompt
            if iteration % (len(self.agents)) == 0:
                self.add_message(prompt)
            # agent_a -> chat -> agent_b
            if self.last_message_is_string:
                self.basic_chat(agent_a, agent_b, self.latest_message)
            # agent_a -> func() -> agent_b
            if self.last_message_is_func_call and self.has_functions(agent_a):
                self.function_chat(agent_a, agent_b, self.latest_message)
            self.spy_on_agents()
        print(f"---------- Organizer Complete (round_robin_conversation) ----------\n\n")
        self.spy_on_agents()
        agents_were_successful, error_message = self.handle_validate_func()
        cost, tokens = self.get_cost_and_tokens()
        conversation_result: ConversationResult = ConversationResult(
            success=agents_were_successful,
            messages=self.messages,
            cost=cost,
            tokens=tokens,
            last_message_str=self.last_message_always_string,
            error_message=error_message,
        )
        return conversation_result


def generate_session_id(raw_prompt: str):
    """
    Example:
    "get jobs with 'Completed' or 'Started' status"
    ->
    "get_jobs_with_Completed_or_Started_status_12_22_22"
    """
    now = datetime.now()
    hours = now.hour
    minutes = now.minute
    seconds = now.second
    short_time_mm_ss = f"{hours:02}_{minutes:02}_{seconds:02}"
    lower_case = raw_prompt.lower()
    no_spaces = lower_case.replace(" ", "_")
    no_quotes = no_spaces.replace("'", "")
    shorter = no_quotes[:30]
    with_uuid = shorter + "_" + short_time_mm_ss
    return with_uuid


def add_cap_ref(
    prompt: str, 
    prompt_suffix: str, 
    cap_ref: str, 
    cap_ref_content: str
) -> str:
    """
    Attaches a capitalized reference to the prompt.
    Example
        prompt = 'Refactor this code.'
        prompt_suffix = 'Make it more readable using this EXAMPLE.'
        cap_ref = 'EXAMPLE'
        cap_ref_content = 'def foo():\n    return True'
        returns 'Refactor this code. Make it more readable using this EXAMPLE.\n\nEXAMPLE\n\ndef foo():\n    return True'
    """
    new_prompt = f"""{prompt} {prompt_suffix}\n\n{cap_ref}\n\n{cap_ref_content}"""
    return new_prompt


def count_tokens(text: str):
    """
    Count the number of tokens in a string.
    """
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


map_model_to_cost_per_1k_tokens = {
    "gpt-4": 0.075,  # ($0.03 Input Tokens + $0.06 Output Tokens) / 2
    "gpt-4-1106-preview": 0.02,  # ($0.01 Input Tokens + $0.03 Output Tokens) / 2
    "gpt-4-1106-vision-preview": 0.02,  # ($0.01 Input Tokens + $0.03 Output Tokens) / 2
    "gpt-3.5-turbo-1106": 0.0015,  # ($0.001 Input Tokens + $0.002 Output Tokens) / 2
}

def estimate_price_and_tokens(text, model="gpt-4"):
    """
    Conservative estimate the price and tokens for a given text.
    """
    # round up to the output tokens
    COST_PER_1k_TOKENS = map_model_to_cost_per_1k_tokens[model]
    tokens = count_tokens(text)
    estimated_cost = (tokens / 1000) * COST_PER_1k_TOKENS
    # round
    estimated_cost = round(estimated_cost, 2)
    return estimated_cost, tokens

