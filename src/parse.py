import json
import requests as req
from tqdm import tqdm
from pathlib import Path
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, query, start_page=0, end_page=5, page_size=50):
        self.papers_urls = []
        self.papers = []

        self.query = query
        self.start_page = start_page
        self.end_page = end_page
        self.page_size = page_size
    
    def _make_query_url(self, start_page):
        return f'https://dl.acm.org/action/doSearch?AllField={self.query}&startPage={start_page}&pageSize={self.page_size}'

    def _make_page_url(self, url):
        return f'https://dl.acm.org{url}'

    def _parse_paper_urls(self):
        for page_n in tqdm(range(self.start_page, self.end_page+1), desc='Parsing urls..'):
            resp = req.get(self._make_query_url(page_n))
            soup = BeautifulSoup(resp.content, 'html.parser')
            links = soup.find_all('span', attrs={'class': ['hlFld-Title']}) # 'hlFld-ContentGroupTitle'
            for link in links:
                self.papers_urls.append(self._make_page_url(link.find('a')['href']))

    def __parse_papers_refs(self, soup):
        refs = []
        ref_block = soup.find('ol', attrs={'class': 'rlist references__list references__numeric'})
        for ref in ref_block.find_all('li', attrs={'class': ['references__item', 'references__item js--toggle']}):
            refs.append(ref.find('span', attrs={'class': 'references__note'}).text)
        return refs

    def _parse_paper(self, url):
        resp = req.get(url)
        soup = BeautifulSoup(resp.content, 'html.parser')
        self.papers.append({
            'abstract': soup.find('div', attrs={'class': 'abstractSection abstractInFull'}).find('p').text,
            'title': soup.find('h1', attrs={'class': 'citation__title'}).text,
            'publish_date': soup.find('span', attrs={'class': 'CitationCoverDate'}).text,
            'conference': soup.find('div', attrs={'class': 'issue-item__detail'}).find('a').text,
            'references': self.__parse_papers_refs(soup),
            'url': url
        })

    def dump_json(self, path):
        with open(path / "papers.json", "w") as f:
            json.dump(self.papers, f, indent=4)
    
    def pipeline(self, path):
        self._parse_paper_urls()
        for url in tqdm(self.papers_urls, desc='Parsing papers..'):
            self._parse_paper(url)
        self.dump_json(path)
        

# def __parse_papers_authors(self, soup):
#         authors = []
#         for author in soup.find_all('li', attrs={'class': 'loa__item'}):
#             authors.append(author.find('a')['title'])
#         return authors

p = Parser('NLP', 0, 0, 20)
data_path = Path('../data/')

p.pipeline(data_path)

# papers = p.papers_urls
# print(len(papers))
