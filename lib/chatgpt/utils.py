import json
import random
from typing import Optional, Union, Any, Dict, List, Callable
from typing_extensions import override

from termcolor import colored
from openai import AssistantEventHandler
from openai.types.beta.threads.runs import ToolCall, ToolCallDelta, RunStep
from ..logger import logger

role_to_color = {
    "system": "red",
    "user": "green",
    "assistant": "light_yellow",
    "function": "magenta",
}


def pprint_conversation(messages: list[object]) -> None:

    for message in messages:
        if message["role"] == "system":
            print(
                colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(
                colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(
                colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(
                colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(
                colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


class EventHandler(AssistantEventHandler):
    def __init__(self, chat_client, functions, extra_function_call_args):
        super().__init__()
        self.chat_client = chat_client
        self.functions = functions
        self.extra_function_call_args = extra_function_call_args
        self.streamId = random.randint(100, 999)

    @override
    def on_event(self, event):
        '''all event emitted from run'''
        # print(f"All events: [{self.streamId}] {event.event}")
        if event.event == 'thread.run.requires_action':
            # When tool_call=function needed, run status will turn 'requires_action'
            self.handle_requires_action(event.data)

    @override
    def on_text_created(self, text) -> None:
        '''Assistant start reply'''
        print(colored(f"\nASSISTANT: ",
              role_to_color['assistant']), end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        '''Assistant reply in progress'''
        print(
            colored(delta.value, role_to_color['assistant']), end="", flush=True)

    # @override
    # def on_tool_call_done(self, tool_call: ToolCall) -> None:
    #     '''Assistant complete getting all info for tool call'''
    #     logger.info("==on_tool_call_done==\n")
    #     logger.info(tool_call)

    def handle_requires_action(self, data):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            resp = self.functions[tool.function.name](
                **self.extra_function_call_args,
                **json.loads(tool.function.arguments)
            )
            tool_outputs.append({
                "tool_call_id": tool.id, "output": resp})

            logger.info(f'func name: {tool.function.name}')
            logger.info(f'func arg: {tool.function.arguments}')
            logger.info(f'func resp: {resp[:500]}')

        self.submit_tool_outputs(tool_outputs)
        return

    def submit_tool_outputs(self, tool_outputs):
        # Use the submit_tool_outputs_stream helper
        with self.chat_client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(self.chat_client, functions=self.functions,
                                       extra_function_call_args=self.extra_function_call_args),
        ) as stream:
            stream.until_done()
            print("\n")


def get_asst(
        chat_client,
        asst_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        model: Optional[str] = None,
        tools=None):
    '''
    Check if there is an asistant with the specified name exist.
    If yes, retreive the object, if not create new.
    Tools to be loaded

    Return
        Assistant object
    '''
    asst_config = dict(
        description=description,
        instructions=instructions,
        model=model,
        tools=tools,
    )
    asst = None
    if asst_id:
        logger.info(f"Retrieving: {asst_id}")
        asst = chat_client.beta.assistants.retrieve(asst_id)
    else:
        logger.info(f'Searching: {name}')
        assts = chat_client.beta.assistants.list(limit=100)
        for a in assts:
            if a.name == name:
                asst = a
                logger.info(f"Found: {asst.name}")
                break
        logger.info(f"Not found: {asst.name}")
    if not asst:
        logger.info(f"Creating: {asst.name}")
        asst = chat_client.beta.assistants.create(name=name, **asst_config)
    else:
        chat_client.beta.assistants.update(asst.id, **asst_config)
    return asst
