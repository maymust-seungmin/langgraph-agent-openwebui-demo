"""
title: Postgres Analyst
author: Seungmin Lee
description: Postgres Analyst
required_open_webui_version: 0.6.5
version: 0.1
licence: MIT
"""

import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../langgraph_agents"))
)

from langgraph_agents.agents.data_analyst import (
    get_llm,
    create_agent_builder,
    Valves,
)

from typing import List, Union, Generator, Iterator
from langchain_core.messages import AIMessage

from langchain_core.messages import convert_to_messages
from langchain_core.messages import messages_to_dict


class Pipeline:
    """
    Data Analyst pipeline.

    This pipeline is a simple LangGraph-based data analyst.

    Valve Parameters: NONE

    """

    class Valves(Valves):
        pass

    def __init__(self):
        self.name = "Postgres Analyst"

        self.valves = self.Valves()

        # Build the agent graph
        self.graph = create_agent_builder(llm=get_llm()).compile()

    async def on_startup(self):
        print(f"on_startup:{self.name}")

    async def on_shutdown(self):
        print(f"on_shutdown:{self.name}")

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        """
        Main pipeline function. Processes user messages through the LangGraph agent.

        Handles conversion between OpenWebUI message format and LangGraph/LangChain message format.
        OpenWebUI format: List of dicts with 'role' and 'content' keys
        LangGraph/LangChain format: List of BaseMessage objects (SystemMessage, HumanMessage, AIMessage, ToolMessage)
        """
        # Convert OpenWebUI messages to LangChain format

        langchain_messages = convert_to_messages(messages)

        payload = {"messages": langchain_messages}
        try:
            results = self.graph.invoke(payload)
            new_messages = results["messages"][len(langchain_messages) :]
        except Exception as e:
            msg = f"Error in pipe: {str(e)}"
            print(msg)
            new_messages = [AIMessage(content=msg)]

        # Convert LangChain messages back to OpenWebUI format
        # openwebui_messages = convert_messages_from_langchain_to_openwebui(new_messages)

        openwebui_messages = messages_to_dict(new_messages)
        for msg in openwebui_messages:
            _data = msg["data"]
            for key, value in _data.items():
                msg[key] = value

            # if body.get("stream", True):
            # logger.debug(f"LangGraph STREAM Response: BELOW")
            # Simulate streaming: yield each message content
        for msg in openwebui_messages:
            if "content" in msg and msg["content"]:
                yield msg["content"] + "\n"
            if "function_call" in msg:
                yield f"[Function Call: {msg['function_call']}]" + "\n"
        # else:
        #     # Join all message contents into one response
        #     response = "\n\n".join(
        #         msg["content"]
        #         for msg in openwebui_messages
        #         if "content" in msg and msg["content"]
        #     )
        #     # logger.debug(f"LangGraph JOIN Response: {response}")
        #     return response
