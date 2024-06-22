import logging
import json
from pathlib import Path
from typing import Optional, Union, Any, Dict, List, Callable

import requests

from .logger import logger


class FileSource(object):
    '''
    Read/Write/Append interface for files (utf-8 encoding)
    '''

    def __init__(self, file_dir: Union[str, Path], format: str = 'unknown'):
        self._e = 'utf-8'  # default encoding for reading/writing files
        self.format = format
        self.file_dir = Path(file_dir)

    def write(self, content: str) -> None:
        '''
        Truncate file, and save new content from unicode string
        '''
        self.file_dir.parent.mkdir(parents=True, exist_ok=True)
        with self.file_dir.open('w', encoding=self._e) as f:
            f.write(content)  # unicode string
        return

    def append(self, content: str) -> None:
        '''
        Append content from unicode string into file
        '''
        with self.file_dir.open('a', encoding=self._e) as f:
            f.write(content)  # unicode string
        return

    def read(self) -> str:
        '''
        Get file content in unicode string (not bytes)
        '''
        with self.file_dir.open('r', encoding=self._e) as f:
            content = f.read()  # unicode string
        return content


class HtmlFile(FileSource):
    '''
    Html file source with clawer that gets html from url and save to file
    '''

    def __init__(self, html_dir: Union[str, Path], url: str, http_headers: Dict[str, str] = {}) -> None:
        self.url = url
        self.http_headers = http_headers
        super().__init__(file_dir=html_dir, format='html')

    def claw(self) -> None:
        """
        Claw html content from url and save to a local directory
        """
        html_content = requests.get(
            self.url, headers=self.headers).text  # unicode string
        self.write(html_content)
        return


class CsvFile(FileSource):
    '''
    Csv file source with a specialized append method that auto handle header in csv file
    '''

    def __init__(self, csv_dir: Union[str, Path], csv_headers: List[str] = []) -> None:
        self.csv_headers = csv_headers
        super().__init__(file_dir=csv_dir, format='csv')

    def append(self, content: str) -> None:
        '''
        append content to csv with handling of csv headers
        create csv file if not already existed
        args:
            content: csv rows (without headers)
        '''
        self.file_dir.parent.mkdir(parents=True, exist_ok=True)
        with self.file_dir.open("a", encoding=self._e) as f:
            if f.tell() == 0:  # empty file i.e. without header row
                f.write(','.join(self.csv_headers) + '\n')
            f.write(content)

        return


class JsonFile(FileSource):
    '''
    Json file source with specialized write, append and read method
    '''

    def __init__(self, json_dir: Union[str, Path]) -> None:
        super().__init__(file_dir=json_dir, format='json')

    def write(self, content: Optional[object]) -> None:
        '''
        Truncate file, and save new python object into json file
        '''
        self.file_dir.parent.mkdir(parents=True, exist_ok=True)
        with self.file_dir.open('w', encoding=self._e) as f:
            json.dump(content, f, indent=2)
        return

    def apend(self, new_items: list[object]) -> None:
        '''
        If json file is a list, append new element to the end of the list
        create a json list file if empty or not already exsited
        args:
            new_items: a list of objects to be appended
        '''
        self.file_dir.parent.mkdir(parents=True, exist_ok=True)
        self.file_dir.touch(exist_ok=True)
        if self.file_dir.stat().st_size == 0:
            new_list = new_items
        else:
            with self.file_dir.open('r', encoding=self._e) as f:
                new_list = json.load(f) + new_items

        with self.file_dir.open('w', encoding=self._e) as f:
            json.dump(new_list, f, indent=2)

        return

    def read(self) -> object:
        '''
        Deserialize json content into python object
        '''
        with self.file_dir.open('r', encoding=self._e) as f:
            content = json.load(f)
        return content
