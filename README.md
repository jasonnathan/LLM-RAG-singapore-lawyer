# LLM based Chatbot with knowledges about Singapore Laws

## Overview

This is an experiemntal project on LLM and RAG that implements an agent that retrieves relevant information from **embedded** Singapore laws via ChatGPT model's **function call**. It

- Uses OpenAI API as _base chatting LLM_;
- Supports OPENAI or Ollama supported LLM as _embedding model_ for RAG.

Several Singapore Laws are clawed for experimental purposes.

Code implementation walks through full lifecycle of RAG, i.e.

1. HTML clawing
2. Formatting to Markdown
3. Chunking
4. Embedding
5. Store into Chroma db
6. Retrieval at chatting via function call

## How to use

1. `pipenv install`
2. Fill `config.py`
3. Embedding is completed using `text-embedding-3-small`, embedding vectors are stored under /data/acts_embedding/text-embedding-3-small
4. Just run `python scripts/embed_sg_acts.py` to save these vectors into Chroma DB
5. Start chat by running `python talk_to_assistant.py`

- \*As of now, the agent is implemented for CLI only

## Configurations (`config.py`)

- Chatting config

  - exit = # User enter this phrase to end chat in CLI
  - tool_choice = # "auto" | "required" | "none" whether assistant should always query Singapore in conversations
  - asst_lawyer = # create a chatgpt assistant with lawyer persona, input assistant id here

- OPENAI model

  - openai_gpt_model = # Model for chatting from chatgpt, e.g. "gpt-3.5-turbo-0125", "gpt-4o-2024-05-13", "gpt-4"
  - openai_api_key = # API key from OpenAI for chatting and embedding

- Embedding model

  - openai_emb_model = # Model for embedding document of Singapore Laws from OpenAI, e.g. "text-embedding-3-small", "text-embedding-3-large"

- Ollama

  - ollama_base_url = # Endpoint of Ollama if embed model is deployed via Ollama. E.g. local ollama can use `http://127.0.0.1:11434`
  - ollama_headers = # Additional header for authentication if Ollama endpoint is protected. E.g. Put {} if no special auth; Put {"authorization": "Bearer xxxx"} if auth by bearer token
  - ollama_llama3_emb_model = # Model for embedding document of Singapore Laws deployed via Ollama. E.g. "llama3:8b"
  - _feel free to use other embedding model deployed via ollama_

- embed_in_use = # The embedding function to be used (Lang Chain's interface for embedding)

- Chroma DB
  - db_path = # Folder path for vector store Chroma. e.g. Path('./db/chroma/')
  - chroma_cll_name = # Chroma DB Collection name to store the Singapore Law embedding data. If embedding function is changed, please change to use a new collection. E.g. f'{embed_in_use.model}-all-sg-acts'
  - lc_cll_in_use = # Chroma DB collection to be used (Lang Chain's interface for vector store)

## Code Structure and Design

- data

  - `acts.csv`: The list of Singapore Laws (aka. Acts) and their urls for clawing
  - `acts_html`: default folder to store the clawed Singapore laws html files
  - `acts_md`: default folder to store the markdown file that is converted from law html files
  - `acts_chunked`: default folder to store the chunked documents from markdown files
  - `acts_embedding`: default folder to store the embedding doc & its vector for each piece of chunked documents (By default, different embedding function should store into a dedicated subfolder to avoid mixing the embedding vectors data)

- db

  - `chroma`: Folder for Chroma DB vector store storing embedding vectors

- lib

  - `file_source.py`: Class for HTML, Json, Csv file sources used to store intermediate processing or embedding data files
  - `html_embedder.py`: Class for embedding text document from HTML files. Making use of `FileSource` and its subclass
  - `utils.py`: miscellaneous functions
  - custom
    - `converter.py`: contain custom converter to convert Singapore Laws HTML file into markdown. _Feel free to add new and override in `HTMLEmbedder` class_
    - `spliter.py`: custom spliter to split Singapore Laws markdown file into Lang chain's Document. _Feel free to add new and override in `HTMLEmbedder` class_
    - `md_formatter.py`: miscellaneous short function for markdown formatting
  - chatgpt
    - `function_calls.py`: Declare functions that can be used in OpenAI chat API tools.
    - `minions.py`: Class for minion. Minion is personalized bot includes starting instructions. SubClass of minion exposes specialized function of each minion.
    - `utils.py`: helper functions specific to OpenAI APIs

- scripts

  - `embed_sg_acts.py`
    - `SGActEmbedder`: HTML Embedder specific for SG Law Acts with an override converter for html to markdown and an override spliter to chunk markdown files
    - run this script to embed the singapore laws again (e.g. when change to a different vector store, using different embedding function and etc)
  - `test_retrieval.py`: Adhoc testing script to check the performance of Vector store search, and relevance search behavior.

- root

  - `talk_to_assistant.py`: Using Assistant API with streaming to launch a chat session with OpenAI chatgpt, incorporating starting prompt and function call tools.
    - _Feel free to implement with other chat LLM_
  - `talk_to_chatgpt.py`: Launch a chat session with OpenAI chatgpt, incorporating starting prompt and function call tools. _Feel free to implement with other chat LLM_
