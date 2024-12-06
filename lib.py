from dataclasses import dataclass, field
import os
import itertools
import collections

import requests
from bs4 import BeautifulSoup
import pandas as pd

import config_file

def get_webpage_html(url:str)->str:
    req = requests.get(url)
    print(req.status_code)
    if req.status_code >= 200 and req.status_code < 500:
        return req.content
    else:
        raise "I did not get the website '{}'.".format(url)
    
def most_frequent1(list_1:list):
    dict = {}
    count, itm = 0, ''
    for item in reversed(list_1):
        dict[item] = dict.get(item, 0) + 1
        if dict[item] >= count :
            count, itm = dict[item], item
    return(itm)

def most_frequent(list_1):
    occurence_count = collections.Counter(list_1)
    return occurence_count.most_common(1)[0][0]

def save_table_data(list1:list, filename='filename.tsv', separator="\t")->None:
    df = pd.DataFrame(list1)
    df.to_csv(filename,sep=separator)

@dataclass
class MyTable:
    webpage_url : str = ""
    html : str = field(repr=False, default="")
    column_titles: list[str] = field(default_factory=list)
    save_file_name : str = 'tsv_data.txt'

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

    def get_webpage_html(self):
        self.html = get_webpage_html(self.webpage_url)

    def load_html_from_file(self, path):
        if isinstance(path, str):
            abs_path = os.path.join(os.getcwd(), path)
            if os.path.exists(abs_path):
                with open(abs_path, mode='r') as in_file:
                    self.html = "\n".join(in_file.readlines())
                    return self.html
            else:
                raise Exception("Cannot find file.")

    def get_webpage_soup(self):
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def get_product_table(self)->list:
        data = list()
        # CSS selectors
        HEADER_ROW_SELECTOR = "RenderableRow_"
        header_rows = self.soup.find_all("tr", {"id": lambda L: L and L.startswith(HEADER_ROW_SELECTOR)})
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
        return data
    
    def save_table_data(self, table_data:list)->None:
        save_table_data(table_data, self.save_file_name, separator='\t')

    def get_table_from_file(self):
        self.load_html_from_file(config_file.html_location)
        self.get_webpage_soup()
        table_data = self.get_product_table()
        self.save_table_data(table_data)

    def test_sample_html(self):
        # Load html from url
        # self.get_webpage_html()
        # Load html from file
        self.load_html_from_file(config_file.html_location)
        # Get the webpage in nice OOP format
        self.get_webpage_soup()
        # This is the webpage made to look nice.
        # print(self.soup.prettify())
        table_data = self.get_product_table()
        self.save_table_data(table_data)