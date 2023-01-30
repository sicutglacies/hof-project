import os
import sys
import json
import time
import requests as req
from tqdm import tqdm
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


class Parser:
    def __init__(self, query, path, start_page=0, end_page=5, page_size=50):
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count() + 4)
        self.path = path

        self.papers_urls = []
        self.papers = []

        self.query = query
        self.start_page = start_page
        self.end_page = end_page
        self.page_size = page_size
    
    def _make_query_url(self, start_page):
        return f'https://dl.acm.org/action/doSearch?AllField={self.query}&startPage={start_page}&pageSize={self.page_size}&sortBy=EpubDate_desc'

    def _make_page_url(self, url):
        return f'https://dl.acm.org{url}'

    def _parse_paper_urls(self):
        for page_n in tqdm(range(self.start_page, self.end_page+1), desc='Parsing urls..'):
            resp = req.get(self._make_query_url(page_n))
            if resp.status_code != 200:
                with open(self.path / f"{self.query}_links.json", "w") as f:
                    json.dump({'links': self.papers_urls}, f, indent=4)
                    sys.exit('Probably your IP is now banned')
            soup = BeautifulSoup(resp.content, 'html.parser')
            links = soup.find_all('span', attrs={'class': ['hlFld-Title']}) # 'hlFld-ContentGroupTitle'
            for link in links:
                self.papers_urls.append(self._make_page_url(link.find('a')['href']))
            time.sleep(0.1)
    
    def _parse_authors_affiliations(self, url):
        time.sleep(0.1)
        resp = req.get(f'{url}/colleagues')
        soup = BeautifulSoup(resp.content, 'html.parser')
        aff_block = soup.find('ul', attrs={'class': 'rlist facet__list'})
        if aff_block is None:
            return None
        return [li.find('a')['title'] for li in aff_block.find_all('li')[1:]]

    def _parse_authors(self, soup):
        authors = []
        author_names = []
        links = []

        for author in soup.find_all('li', attrs={'class': 'loa__item'}):
            links.append(author.find('div', attrs={'class': 'author-info__body'}).a['href'])
            author_names.append(author.find('a')['title'])

        for author, link in zip(author_names, links):
            author_dict = {'name': author}
            if not link.startswith('/profile'):
                author_dict['link'] = link
                authors.append(author_dict)
                continue
            link = f'https://dl.acm.org{link}'
            author_dict['link'] = link
            resp = req.get(link)
            pub_soup = BeautifulSoup(resp.content, 'html.parser')
            pubs = pub_soup.find_all('div', attrs={'class': 'bibliometrics__block'})
            for pub in pubs:
                if pub.div.text in ['Publication counts', 'Citation count', 'Downloads (12 months)', 'Downloads (cumulative)']:
                    author_dict[pub.div.text] = pub.find('div', attrs={'class': 'bibliometrics__count'}).span.text
                author_dict['affiliations'] = self._parse_authors_affiliations(link)
            authors.append(author_dict)
            time.sleep(0.1)
        return authors

    def __parse_papers_refs(self, soup):
        refs = []
        ref_block = soup.find('ol', attrs={'class': 'rlist references__list references__numeric'})
        if ref_block is None:
            return None
        for ref in ref_block.find_all('li', attrs={'class': ['references__item', 'references__item js--toggle']}):
            ref_text = ref.find('span', attrs={'class': 'references__note'}).text
            refs.append(ref_text)
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
            'url': url,
            'authors': self._parse_authors(soup)
        })

    def dump_json(self):
        with open(self.path / f"{self.query}.json", "w") as f:
            json.dump(self.papers, f, indent=4)
    
    def pipeline(self):
        self._parse_paper_urls()
        with open(self.path / f"{self.query}_links.json", "w") as f:
            json.dump({'links': self.papers_urls}, f, indent=4)

        for url in tqdm(self.papers_urls, desc='Parsing papers..'):
            try:
                self._parse_paper(url)
            except Exception as e:
                print(e)
                print('Probably your IP is now banned')
                break
        self.dump_json()
        # with self.executor as pool:
        #     _ = list(tqdm(pool.map(self._parse_paper, self.papers_urls), total=len(self.papers_urls), desc='Parsing papers..'))

Parser('NLP', Path('../data/'), 0, 10, 50).pipeline()
