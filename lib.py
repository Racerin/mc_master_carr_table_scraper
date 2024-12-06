from dataclasses import dataclass, field
import os
import collections
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd

import config_file

def get_webpage_html(url:str)->str:
    req = requests.get(url)
    if req.status_code >= 200 and req.status_code < 500:
        return req.content
    else:
        raise "I did not get the website '{}'.".format(url)

def most_frequent1(list_1):
    occurence_count = collections.Counter(list_1)
    return occurence_count.most_common(1)[0][0]

def most_frequent(list_1:list):
    dict = {}
    count, itm = 0, ''
    for item in reversed(list_1):
        dict[item] = dict.get(item, 0) + 1
        if dict[item] >= count :
            count, itm = dict[item], item
    return(itm)

def save_table_data(list1:list, filename='filename.tsv', separator="\t")->None:
    df = pd.DataFrame(list1)
    df.to_csv(filename, sep=separator)

@dataclass
class MyTable:
    save_file_name : str = 'tsv_data.tsv'
    save_file_separator :str = '\t'
    column_titles: list[str] = field(default_factory=list)
    webpage_url : str = ""
    html_file_path : str = ""
    html : str = field(repr=False, default="")
    table_data : list[str] = field(default_factory=list)

    def _config_get_text_in_file(self, path:str):
        if path and isinstance(path, str):
            abs_path = os.path.join(os.getcwd(), config_file.html_location)
            if os.path.exists(abs_path):
                with open(abs_path, 'r') as in_file:
                    text = "\n".join(in_file.readlines())
                    return text

    def __init_config(self):
        """Bring-over config.py property values if valid, else keep the current property value."""
        # default values from file
        config_html = self._config_get_text_in_file(config_file.html_location)
        self.html = self.html if config_html is None else config_html
        # default values
        self.webpage_url = config_file.webpage_url if bool(config_file.webpage_url) else self.webpage_url
        # self.webpage_html = config.html if bool(config.html) else self.webpage_html

    def __post_init__(self):
        # Do config initialization
        self.__init_config()

    def get_webpage_html(self)->str:
        self.html = get_webpage_html(self.webpage_url)
        return self.html

    def load_html_from_file(self)->list:
        abs_path = os.path.join(os.getcwd(), self.html_file_path)
        if os.path.exists(abs_path):
            with open(abs_path, mode='r') as in_file:
                self.html = "\n".join(in_file.readlines())
                return self.html
        else:
            raise Exception("Cannot find file.")

    def get_html_soup(self)->BeautifulSoup:
        self.soup = BeautifulSoup(self.html, 'html.parser')
        return self.soup

    def get_main_product_table(self)->list:
        data = list()
        # CSS selectors
        HEADER_ROW_SELECTOR = "RenderableRow_"
        header_rows = self.soup.find_all("tr", {"id": lambda L: L and L.startswith(HEADER_ROW_SELECTOR)})
        assert len(header_rows) > 0, "Didn't find any header_rows."
        # Get the main parent by counting the most frequent parent tag.
        potential_parent_tags = [header_row.parent for header_row in header_rows]
        parent_tag = most_frequent(potential_parent_tags)   # Only develop data for table with most headers.
        tr_tags = parent_tag.find_all('tr')
        column_1 = ""   # At times, there is a header row that defines the rows that come after it. 
            # Include this header row within the consecutive rows' data
        for tr_tag in tr_tags:
            if tr_tag.get('id',"").startswith(HEADER_ROW_SELECTOR):
                column_1 = tr_tag.text
            td_texts = [td.text for td in tr_tag.find_all('td')]
            td_texts.insert(0,column_1)
            data.append(td_texts)
        self.table_data = data
        return data
    
    def save_table_data(self)->None:
        save_table_data(self.table_data, self.save_file_name, separator=self.save_file_separator)

    def get_table_from_file(self)->None:
        html = self.load_html_from_file()
        soup = self.get_html_soup()
        table_data = self.get_main_product_table()
        self.save_table_data()

    def get_table_from_webpage(self)->None:
        html = self.get_webpage_html()
        soup = self.get_html_soup()
        table_data = self.get_main_product_table()
        self.save_table_data()