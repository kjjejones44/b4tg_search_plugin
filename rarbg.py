# VERSION: 1.01
# AUTHORS: kjjejones44

from html.parser import HTMLParser
from urllib.parse import urljoin
import helpers
from novaprinter import prettyPrinter
import re

class rarbg(object):
    
    url = "https://rarbg.to/"
    name = "rarbg"
    
    supported_categories = {'all': [], 'movies': [14, 17, 42, 44, 45, 46, 47, 48, 50, 51, 52, 54], 'tv': [18, 41, 49], 'music': [23, 24, 25, 26], 'games': [27, 28, 29, 30, 31, 32, 40], 'software': [33]}

    def __init__(self): 
        helpers.headers["Cookie"] = "tcc; gaDts48g=q8h5pp9t; aby=2; skt=WA28Vph1yq; skt=WA28Vph1yq; gaDts48g=q8h5pp9t; expla=2"     
    
    class MyHTMLParser(HTMLParser):

        def __init__(self):
            super().__init__()
            self.is_in_table = False
            self.is_in_entry = False
            self.td_index = -1
            self.b_value = ""
            self.temp_result = {}
            self.results = []
            self.current_tag = ()

        def get_results(self):
            return self.results


        def handle_starttag(self, tag, attrs):
            attr_dict = {x[0]:x[1] for x in attrs}
            self.current_tag = (tag, attr_dict)
            if tag == "table":
                if not self.is_in_table and attr_dict.get("class", "") == "lista2t":
                    self.is_in_table = True
            elif tag == "tr" and attr_dict.get("class", "") == "lista2":
                if self.is_in_table:
                    self.is_in_entry = True
            elif tag == "td":
                if self.is_in_entry:
                    self.td_index = self.td_index + 1                    

        def handle_endtag(self, tag):        
            if tag == "tr":                
                self.is_in_entry = False                
                self.td_index = -1

        def handle_data(self, data):
            if self.td_index in range(1, 6):
                if self.td_index == 1 and "title" in self.current_tag[1]:
                    self.temp_result = {
                        "title": self.current_tag[1]["title"],
                        "href": self.current_tag[1]["href"]
                        }
                elif self.td_index == 3:
                    self.temp_result["filesize"] = data
                elif self.td_index == 4:
                    self.temp_result["seeders"] = data
                elif self.td_index == 5:
                    self.temp_result["leechers"] = data
                    self.results.append(self.temp_result)


    def search(self, term, cat="all"):
        pagenumber = 1
        while pagenumber <= 10:
            result_page = self.search_page(term, pagenumber, cat)            
            self.pretty_print_results(result_page)
            if len(result_page) < 15 or int(result_page[-1]['seeders']) < 1:
                break
            pagenumber = pagenumber + 1

    def search_page(self, term, pagenumber, cat):
        try:
            cat_string = "".join([f"&category%5B%5D={x}" for x in self.supported_categories.get(cat, "")])
            query = f"{self.url}torrents.php?search={term}&order=seeders&by=DESC&page={pagenumber}{cat_string}"
            parser = self.MyHTMLParser()
            text = helpers.retrieve_url(query)
            parser.feed(text)
            return parser.get_results()
        except Exception as e:
            return []
        
    def download_torrent(self, info):
        html = helpers.retrieve_url(info)
        magnet = re.search("magnet:\?[^\"]*(?=\")", html).group()
        print(magnet + ' ' + info)

    def pretty_print_results(self, results):
        for result in results:
            temp_result = {
                'name': result['title'],
                'size': result['filesize'],
                'seeds': result['seeders'],
                'leech': result['leechers'],
                'engine_url': self.url,
                'link': urljoin(self.url, result['href'])
            }
            prettyPrinter(temp_result)

if __name__ == "__main__":
    rarbg().search("godzilla")
