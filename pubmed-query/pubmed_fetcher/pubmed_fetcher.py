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
        print("Response data",json_data)

        return json_data["esearchresult"]["idlist"]
    '''
    Method to fetch the paper details from pubmed using the pubmed ids
    '''

    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[Dict[str,str]]:
        if not pubmed_ids:
            print(" No Pubmed ids found")
            return []
        
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
    
    '''
    Method to parse the paper details in the Required format 
    '''

    def parse_pubmed_json(self, json_data: Dict[str, any]) -> List[Dict[str,str]]:

        if "result" not in json_data:
            raise ValueError("❌ Missing 'result' key in PubMed response!")
        papers =[]

        for uid, paper_id in json_data["result"].items():
            if uid =="uids":
                continue

            if not isinstance(paper_id, dict):  
                print(f"⚠️ Skipping invalid entry: {uid}")  
                continue  

            pubmed_id = paper_id.get('uid')
            title = paper_id.get('title', '')
            publication_date = paper_id.get('pubdate','')

            authors = paper_id.get('authors', [])
            print(f"pubmed ID {uid} - Authors: {authors}")

            non_academic_authors = [
                author['name']
                for author in authors 
                if 'university' not in author.get('affiliation','').lower()
                ]
            
            company_affiliations = [
            author['affiliation']
            for author in authors
            if any(keyword in author.get('affiliation', '').lower() for keyword in ['pharma', 'biotech', 'inc', 'ltd', 'corp', 'gmbh','research','company', 'pharamceutical','laboratories','company'])
            ]

            #company_affiliations = [author['affiliation'] for author in authors if 'pharma' in author.get('affiliation','').lower()]
            corresponding_author_email= paper_id.get('corresponding_author',{}).get('email', '')

            if company_affiliations:
                papers.append(
                    {
                        'PubmedID': pubmed_id,
                        'Title' : title,
                        'Publication Date': publication_date,
                        'Non-academic Author(s)': non_academic_authors,
                        'Company Affiliation(s)' : company_affiliations,
                        'Corresponding Author Email': corresponding_author_email
                    }
                )
        if not papers:
            print("No Matching papers found with the company affiliations")
        return papers
    
    '''
    Method to sacve the paper details in the CSV file
    '''

    def save_to_csv(self, data: List[Dict[str,str]],filename:str): # here data is paper detail method obj 
        if not data:
            print("⚠️ No data to save!")
            return
        with open(filename, 'w' , newline='', encoding='utf-8') as csvfile:
            filednames = ['PubmedID', 'Title', 'Publication Date', 'Non-academic Author(s)','Company Affilication(s)','Corresponding Author Email']
            # writing the header and data rows
            writer = csv.DictWriter(csvfile, fieldnames=filednames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
