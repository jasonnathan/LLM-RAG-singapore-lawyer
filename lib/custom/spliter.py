import logging
from typing import Optional, Union, Any, Dict, Callable

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

logger = logging.getLogger("sg_acts_kb")


chunk_size = 2000
chunk_overlap = 100


def md_split_sg_acts(md: str) -> list[Document]:
    '''
    split act by header into pieces
    returns:
        splits (list of dict): python object which includes list of doc and metadata
    '''
    headers_to_split_on = [
        ("#", "Law"),
        ("##", "Part"),
        ("###", "Provision"),
    ]
    try:
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on)
        md_header_splits = markdown_splitter.split_text(md)
    except Exception as e:
        logger.error(str(e))

    try:
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        text_splits = text_splitter.split_documents(md_header_splits)
    except Exception as e:
        logger.error(str(e))

    for d in text_splits:
        d.page_content = \
            f"{' >> '.join(d.metadata.values())}: {d.page_content}"
    return text_splits
