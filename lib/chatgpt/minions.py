# from .utils import chat_completion_request
from ..logger import logger
from typing import Optional, Union, Any, List, Dict, Callable
from tenacity import retry, wait_random_exponential, stop_after_attempt


class Prompt(object):
    def __init__(self, sentences: List[str]):
        self._sentences = sentences

    @property
    def instructions(self) -> str:
        return " ".join(self._sentences)

    @property
    def messages(self) -> List[object]:
        return [
            {"role": "system", "content": s} for s in self._sentences
        ]


class Minion(object):
    def __init__(self, name: str, description: str, sentences: List[str], model: str, chat_client: Any):
        self.name = name
        self.description = description
        self.model = model
        self.chat_client = chat_client
        self.prompt = Prompt(sentences)

    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def help_me(
            self,
            messages: List[object],
            tool_choice: Union[str, None] = "auto",
            tools: Union[List[object], None] = None) -> str:
        try:
            if tools:
                response = self.chat_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tool_choice=tool_choice,
                    tools=tools,
                )
            else:
                response = self.chat_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
            return response
        except Exception as e:
            logger.error(f"Unable to generate ChatCompletion response: {e}")
            logger.error(f'Response: {response}')
            return e


class MnLawyer(Minion):
    def __init__(self, name: str, model: str, chat_client: Any):
        description = "Singapore Lawyer"
        sentences = [
            "User need help with sinagpore laws. You are a lawyer to interpret the laws and advice users accordingly.",
            "Please try to use layman terms where needed.",
        ]
        super().__init__(name, description, sentences, model, chat_client)


class MnRelevanceChecker(Minion):
    def __init__(self, name: str, model: str, chat_client: Any):
        description = "Checker for relevance of Query and additional information"
        sentences = [
            "You are given a question and a piece of additional information.",
            "Assess if the additional info is useful to you if you are to answer the question. Answer 'yes' or 'no'.",
            # "If no, why not useful?",
            # "Assess if  the additional info is related to the question. Answer 'yes' or 'no', if no, why not related?",
        ]
        super().__init__(name, description, sentences, model, chat_client)

    def filter_relevant_results(self, results: List[str], query: str) -> List[str]:
        relevant_results = []
        messages = self.prompt.messages

        messages.append({"role": "user", "content": f'## Question: {query}'})
        messages.append({"role": "user", "content": "dummy"})
        for r in results:
            messages[-1] = {"role": "user",
                            "content": f'## Additional info:\n{r}'}
            chat_response = self.help_me(messages)
            assistant_message = chat_response.choices[0].message

            logger.info(
                f'RelevanceChecker: {r[:70]} ===> {assistant_message.content}')
            if "yes" in assistant_message.content.lower():
                relevant_results.append(r)

        return relevant_results


class MnKeywordFinder(Minion):
    def __init__(self, name: str, model: str, chat_client: Any):
        description = "Identify keywords to search from queries."
        sentences = [
            "You are given a query that user wants to get an answer from some documents.",
            "To optimize the search, think of a combination of key words that may appear in the relevant sections of document.",
            "Also replace any short term with full terms. e.g. GST as Good and service tax.",
            "Output key words or phrases separated by comma.",
        ]
        super().__init__(name, description, sentences, model, chat_client)

    def think_of_keywords_to_search(self, query: str) -> list[str]:
        messages = self.prompt.messages

        messages.append({"role": "user", "content": f'## Question: {query}'})
        chat_response = self.help_me(messages)
        assistant_message = chat_response.choices[0].message

        keywords = assistant_message.content.lower().split(',')
        logger.info(f'KeywordFinder: {query} ===> {keywords}')
        return keywords
