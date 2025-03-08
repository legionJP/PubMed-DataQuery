import requests
from typing import List, Dict
import csv


class PubmedFetcher:
    def fetch_pubmed_ids(self, query:str) -> List[str]:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": 100,
            "retmode": "json",
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        json_data = response.json()
        return json_data["esearchresult"]["idlist"]
    
    '''
    Method to fetch the paper details from pubmed using the pubmed ids
    '''

    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[Dict[str,str]]:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(pubmed_ids),
            "retmode": "json",
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return self.parse_pubmed_json(data)
    
    def parse_pubmed_json(self, json_data: Dict[str, any]) -> List[Dict[str,str]]:
        papers =[]
        for uid, papers in json_data['results'].items():
            if uid =="uids":
                continue
            pubmed_id = papers.get('uid')
            title = papers.get('title', '')
            publication_date = papers.get('pubdate','')
            authors = papers.get('authors', [])
            