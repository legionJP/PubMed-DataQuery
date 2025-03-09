import requests
from typing import List, Dict, Any
import csv

class PubMedFetcher:
    def fetch_pubmed_ids(self, query:str) -> List[str]:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": 1000,
            "retmode": "json",
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        json_data = response.json()

        if self.debug:
            print("Response Dats",json_data)
        return json_data["esearchresult"]["idlist"]
    '''
    Method to fetch the paper details from pubmed using the pubmed ids
    '''

    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[Dict[str,Any]]:
        if not pubmed_ids:
            if self.debug:
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

    def parse_pubmed_json(self, json_data: Dict[str, Any]) -> List[Dict[str,Any]]:

        if "result" not in json_data:
            raise ValueError("❌ Missing 'result' key in PubMed response!")
        
        papers: List[Dict[str,Any]] =[]

        company_keywords = [
            'pharma', 'biotech', 'inc', 'ltd', 'corp', 'gmbh', 'company',
            'pharmaceutical', 'laboratories', 'corporation', 'biosciences', 'therapeutics',
            'bio', 'llc', 'limited', 'biopharmaceutics', 'pfizer', 'novartis', 'roche',
            'merck', 'gsk', 'abbvie', 'amgen', 'bms', 'j&j'
        ]
        academic_keywords = ['university', 'institute', 'college', 'hospital']

        for uid, paper_info in json_data["result"].items():
            if uid =="uids":
                continue

            if not isinstance(paper_info, dict):
                if self.debug:  
                    print(f"⚠️ Skipping invalid entry: {uid}")  
                continue  

            pubmed_id = paper_info.get('uid', '')
            title = paper_info.get('title', '')
            publication_date = paper_info.get('pubdate','')

            authors = paper_info.get('authors', [])
           # print(f"pubmed ID {uid} - Authors: {authors}")

            non_academic_authors = [
                author.get('name', '')
                for author in authors 
                if not any (academic_kw in author.get('affiliation', '').lower() for academic_kw in academic_keywords)
            ]
        
            # company_affiliations = [
            #     author['affiliation']
            #     for author in authors
            #     if any(keyword in author.get('affiliation', '').lower() for keyword in company_keywords)
            # ]
            company_affiliations = []
            for author in authors:
                affiliation = author.get('affiliation', '')
                if affiliation and any(keyword in affiliation.lower() for keyword in company_keywords):
                    company_affiliations.append(affiliation)

            if self.debug:
                print(f"Paper {pubmed_id} - Company Affiliations: {company_affiliations}")
            #company_affiliations = [author['affiliation'] for author in authors if 'pharma' in author.get('affiliation','').lower()]
            
            # Only include the paper if at least one company affiliation is present
            if company_affiliations:
                corresponding_author_email= paper_info.get('corresponding_author',{}).get('email', '')
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
        if self.debug and not papers:
            print("No Matching papers found with the company affiliations")
        return papers
    
    '''
    Method to sacve the paper details in the CSV file
    '''

    def save_to_csv(self, data: List[Dict[str,Any]],filename:str) -> None: # here data is paper detail method obj 
        if not data:
            print("⚠️ No data to save!")
            return
        fieldnames = [ 'PubmedID',
                       'Title', 
                       'Publication Date',
                       'Non-academic Author(s)',
                       'Company Affilication(s)',
                       'Corresponding Author Email'
        ]

        with open(filename, 'w' , newline='', encoding='utf-8') as csvfile:
            # writing the header and data rows
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                # Convert list values into semicolon-separated strings
                row_copy = row.copy()
                if isinstance(row_copy.get('Non-academic Author(s)'), list):
                    row_copy['Non-academic Author(s)'] = '; '.join(row_copy['Non-academic Author(s)'])
                if isinstance(row_copy.get('Company Affiliation(s)'), list):
                    row_copy['Company Affiliation(s)'] = '; '.join(row_copy['Company Affiliation(s)'])
                writer.writerow(row_copy)



## Code 2
# import requests
# from typing import List, Dict, Any
# import csv
# import re

# class PubMedFetcher:
#     def fetch_pubmed_ids(self, query: str, retmax: int = 1000) -> List[str]:
#         """
#         Fetch PubMed IDs based on the search query.

#         Args:
#             query (str): The search query.
#             retmax (int): The maximum number of results per request.

#         Returns:
#             List[str]: A list of PubMed IDs.
#         """
#         url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
#         params = {
#             "db": "pubmed",
#             "term": query,
#             "retmax": retmax,
#             "retmode": "json",
#         }
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         json_data = response.json()
#         print("Response data:", json_data)

#         return json_data["esearchresult"]["idlist"]

#     def post_ids_to_history(self, pubmed_ids: List[str]) -> tuple[str, str]:
#         url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/epost.fcgi"
#         params = {
#             "db": "pubmed",
#             "id": ",".join(pubmed_ids)
#         }
#         response = requests.post(url, data=params)
#         response.raise_for_status()
#         xml_data = response.text
#         webenv = re.search(r"<WebEnv>(\S+)</WebEnv>", xml_data).group(1)
#         query_key = re.search(r"<QueryKey>(\d+)</QueryKey>", xml_data).group(1)
#         return webenv, query_key

#     def fetch_paper_details_from_history(self, webenv: str, query_key: str, retstart: int = 0, retmax: int = 200) -> List[Dict[str, str]]:
#         url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
#         params = {
#             "db": "pubmed",
#             "query_key": query_key,
#             "WebEnv": webenv,
#             "retstart": retstart,
#             "retmax": retmax,
#             "retmode": "json",
#         }
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         data = response.json()
#         return self.parse_pubmed_json(data)

#     def parse_pubmed_json(self, json_data: Dict[str, Any]) -> List[Dict[str, str]]:
#         """
#         Parse the PubMed JSON response and extract paper details.

#         Args:
#             json_data (Dict[str, Any]): The JSON data from PubMed.

#         Returns:
#             List[Dict[str, str]]: A list of dictionaries containing paper details.
#         """
#         if "result" not in json_data:
#             raise ValueError("❌ Missing 'result' key in PubMed response!")
#         papers = []

#         for uid, paper_info in json_data["result"].items():
#             if uid == "uids":
#                 continue

#             if not isinstance(paper_info, dict):
#                 print(f"⚠️ Skipping invalid entry: {uid}")
#                 continue

#             pubmed_id = paper_info.get('uid')
#             title = paper_info.get('title', '')
#             publication_date = paper_info.get('pubdate', '')

#             authors = paper_info.get('authors', [])
#             print(f"PubMed ID {uid} - Authors: {authors}")

#             non_academic_authors = [
#                 author['name']
#                 for author in authors
#                 if 'university' not in author.get('affiliation', '').lower()
#             ]

#             company_keywords = [
#                 'pharma', 'biotech', 'inc', 'ltd', 'corp', 'gmbh', 'research',
#                 'company', 'pharmaceutical', 'laboratories', 'corporation', 'research institute', 'biosciences', 'therapeutics', 'bio', 'llc', 'limited', 'industries', 'technologies'
#             ]

#             company_affiliations = [
#                 author.get('affiliation', '')
#                 for author in authors
#                 if any(keyword in author.get('affiliation', '').lower() for keyword in company_keywords)
#             ]

#             corresponding_author_email = paper_info.get('corresponding_author', {}).get('email', '')

#             print(f"Company Affiliations for PubMed ID {uid}: {company_affiliations}")

#             if company_affiliations:
#                 papers.append(
#                     {
#                         'PubmedID': pubmed_id,
#                         'Title': title,
#                         'Publication Date': publication_date,
#                         'Non-academic Author(s)': ', '.join(non_academic_authors),
#                         'Company Affiliation(s)': ', '.join(company_affiliations),
#                         'Corresponding Author Email': corresponding_author_email
#                     }
#                 )

#         if not papers:
#             print("No matching papers found with company affiliations.")
#         return papers

#     def save_to_csv(self, data: List[Dict[str, str]], filename: str):
#         """
#         Save the paper details to a CSV file.

#         Args:
#             data (List[Dict[str, str]]): A list of dictionaries containing paper details.
#             filename (str): The name of the output CSV file.
#         """
#         if not data:
#             print("⚠️ No data to save!")
#             return

#         with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
#             fieldnames = ['PubmedID', 'Title', 'Publication Date', 'Non-academic Author(s)', 'Company Affiliation(s)', 'Corresponding Author Email']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writeheader()
#             for row in data:
#                 writer.writerow(row)

# # Example Usage
# fetcher = PubMedFetcher()
# query = "pharmaceutical company OR biotech company AND 2021[DP]"
# pubmed_ids = fetcher.fetch_pubmed_ids(query)
# webenv, query_key = fetcher.post_ids_to_history(pubmed_ids)

# # Fetch details in batches
# retstart = 0
# retmax = 200
# all_details = []

# while True:
#     details_batch = fetcher.fetch_paper_details_from_history(webenv, query_key, retstart, retmax)
#     if not details_batch:
#         break
#     all_details.extend(details_batch)
#     retstart += retmax

# fetcher.save_to_csv(all_details, "pubmed_results.csv")
# print(all_details)
