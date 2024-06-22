import os
from pathlib import Path
import logging

import chromadb
from chromadb.config import Settings
# from langchain_chroma import Chroma
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from lib.logger import logger

# chatting config
exit = "bye"
asst_lawyer = "asst_xxxxx"
tool_choice = "auto"

# gpt model
openai_gpt_model = "gpt-4o"  # "gpt-3.5-turbo-0125"
openai_api_key = "xxxxx"
openai_chat = OpenAI(
    api_key=openai_api_key
)

# embedding model
openai_emb_model = "text-embedding-3-small"
openai_embed = OpenAIEmbeddings(
    model=openai_emb_model, openai_api_key=openai_api_key)

ollama_base_url = "http://127.0.0.1:11434"  # "https://llm.xuyangbo.com"
ollama_headers = {"authorization": "xxxxx"}  # optional header
ollama_llama3_emb_model = "llama3:8b"
ollama_llama3_embed = OllamaEmbeddings(
    model=ollama_llama3_emb_model, base_url=ollama_base_url, headers=ollama_headers)

embed_in_use = openai_embed


# chroma db
db_path = Path('./db/chroma/')
db_path.mkdir(parents=True, exist_ok=True)
chroma_client = chromadb.PersistentClient(
    path=str(db_path), settings=Settings(anonymized_telemetry=False))
chroma_cll_name = f'{embed_in_use.model}-all-sg-acts'

lc_cll_in_use = Chroma(
    client=chroma_client,
    collection_name=chroma_cll_name,
    embedding_function=embed_in_use,
)
