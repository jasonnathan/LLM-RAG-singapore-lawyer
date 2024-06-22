import logging
import urllib.parse
import requests

from langchain_core.vectorstores import VectorStore
from ..logger import logger


def retrieve_sg_acts(**args) -> str:
    '''
    Use this function if assistant does not have sufficient knowledge on singapore laws and acts. 
    Based on key terms or words in user query, search the relevant additional information from 
    external data sources. You need to replace abbreviation in users question with full terminology

    args:
        key_words: list of key words to search embedding
        query: original question from user
        lc_vs: lang chain vector store object

        no_filter: whether to apply relevance filter
        chat_client: chat client for relevance filter
        model: chat model for relevance filter
    returns:
        results concatenated by /n/n
    '''
    def search_vs(lc_vs: VectorStore, text: str, k: int) -> list[str]:
        docs = lc_vs.similarity_search_with_score(text, k)
        results = [d.page_content for d, score in docs]
        return results

    myKwFinder = args['kw_finder']
    myRelChecker = args['relv_checker']

    key_words = myKwFinder.think_of_keywords_to_search(args['query'])

    # results = search_vs(args['lc_vs'], ", ".join(args['key_words']), 10)
    results = search_vs(args['lc_vs'], ", ".join(key_words), 10)
    # logger.info(f"From outside: {args['key_words']}")

    if ('no_filter' in args and args['no_filter']) == False:
        results = myRelChecker.filter_relevant_results(results, args['query'])

    return "\n\n".join(results)


functions = {
    "declaration": {
        "retrieve_sg_acts": retrieve_sg_acts,
    },
    "description": [
        {
            "type": "function",
            "function": {
                "name": "retrieve_sg_acts",
                "description": "Call this function if assistant does not have sufficient knowledge on singapore laws and acts. Based on key terms or words in user query, search the relevant additional information from external data sources. You need to replace abbreviation in users question with full terminology, e.g. CPF as Central Provident Fund.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "User's question that we want to search the additional information for. You need to replace abbreviation in users question with full terminology, e.g. CPF as Central Provident Fund."
                        },
                        "key_words": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "The list of key terms or words to search for that are extracted from user query. You need to replace abbreviation with full terminology, e.g. CPF as Central Provident Fund.",
                            }
                        }
                    },
                    "required": ["query", "key_words"],
                },
            },
        },
    ]
}
