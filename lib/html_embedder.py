import logging
import hashlib
from typing import Optional, Union, Any, Dict, Callable
from pathlib import Path

from langchain_core.documents import Document
from .file_source import HtmlFile, CsvFile, JsonFile, FileSource
from .logger import logger


class HtmlEmbedder(object):
    '''
    This class abstracts an HTML data source, and facilitate the embedding of the data source for LLM consumption.

    1. Store the original HTML data source ultimately for data embedding.

    2. Convert to Md: from html, convert to Mark down and save to folder
        - custom conversion function can be supplied/override

    3. Chunk Md: Chunk md into pieces (as json) and save to folder
        - custom split function can be supplied/override

    4. Embed: embed the chunked md and save the embed data to folder
        - embed function need to be supplied
    '''

    def __init__(self, name: str,
                 original_file: FileSource,

                 md_converter: Callable[[str], str] = lambda x: x,
                 md_splitter: Callable[[str], list[Document]] = lambda x: x,
                 embed_func: Callable = None,
                 ):
        self._e = 'utf-8'  # default encoding for reading/writing html and markdown text

        self.name = name
        self.original_file = original_file

        self._md_converter = md_converter
        self._md_splitter = md_splitter
        self._embed_func = embed_func

        self._md_file, self._chunk_json, self._embed_json = None, None, None

    @property
    def md_file(self) -> Union[FileSource, None]:
        # markdown file generated from original filesource
        return self._md_file

    @md_file.setter
    def md_file(self, fs: Union[FileSource, None]) -> None:
        self._md_file = fs
        return

    @property
    def chunk_json(self) -> Union[JsonFile, None]:
        # chunk file in json generated from markdown filesource
        return self._chunk_json

    @chunk_json.setter
    def chunk_json(self, jf: Union[JsonFile, None]) -> None:
        self._chunk_json = jf
        return

    @property
    def embed_json(self) -> Union[JsonFile, None]:
        # csv file containing embedding vectors and text
        return self._embed_json

    @embed_json.setter
    def embed_json(self, jf: Union[JsonFile, None]) -> None:
        self._embed_json = jf
        return

    def convert_html_to_md(self, save_to_folder: Union[str, Path]) -> None:
        '''
        Based on the html content structure, write into structured markdown file
        '''

        html_content = self.original_file.read()
        md_content = self._md_converter(html_content)

        md_dir = Path(save_to_folder) / f"{self.name}.md"
        self.md_file = FileSource(md_dir, format='md')
        self.md_file.write(md_content)
        return

    def chunk_md(self, save_to_folder: Union[str, Path]) -> None:
        '''
        Split Md file into chunks
        '''
        md_content = self.md_file.read()
        chunk_content = self._md_splitter(md_content)
        logger.info(f'chunked into: {len(chunk_content)}')

        chunk_dir = Path(save_to_folder) / f"{self.name}.json"
        content = [d.dict() for d in chunk_content]
        self.chunk_json = JsonFile(chunk_dir)
        self.chunk_json.write(content)
        return

    def embed(self, save_to_folder: Union[str, Path]) -> None:
        if self._embed_func is None:
            logger.warning("No embedding function specified.")
            return

        embed_dir = Path(save_to_folder) / f"{self.name}.json"

        embed_json = self.chunk_json.read()
        embs = self._embed_func.embed_documents(
            [d['page_content'] for d in embed_json])

        for i, e in enumerate(embs):
            embed_json[i]['embedding'] = e
            embed_json[i]['model'] = self._embed_func.model
            embed_json[i]['id'] = hashlib.sha256(
                embed_json[i]['page_content'].encode('utf-8')).hexdigest()

        self.embed_json = JsonFile(embed_dir)
        self.embed_json.write(embed_json)

        return
