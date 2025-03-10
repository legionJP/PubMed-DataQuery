import requests
from typing import List, Dict, Any
import pandas as pd
import re
import xml.etree.ElementTree as ET
import time  # For introducing sleep intervals

class PubMedFetcher:
    def __init__(self, debug: bool = False) -> None:
        self.debug = debug

    '''
    Method to fetch the ids from esearch based on query , adding the debug and retry as 
    for loop for 3 attempt to fetch data and handle the data request exceptions.
    '''

    def fetch_pubmed_ids(self, query: str) -> List[str]:
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": 0,
            "retmode": "json",
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        json_data = response.json()
        total_count = int(json_data["esearchresult"]["count"])
        if self.debug:
            print(f"Total matching records: {total_count}")
        all_ids: List[str] = []
        retmax = 100
        for start in range(0, total_count, retmax):
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": retmax,
                "retstart": start,
                "retmode": "json",
            }
            if self.debug:
                print(f"Fetching records from {start} to {start + retmax}")
            for attempt in range(3):  # Retry up to 3 times
                try:
                    response = requests.get(base_url, params=params)
                    response.raise_for_status()
                    json_data = response.json()
                    ids = json_data["esearchresult"]["idlist"]
                    all_ids.extend(ids)
                    time.sleep(1)
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < 2:
                        print(f"Retrying due to error: {e}")
                        time.sleep(2 ** attempt)
                    else:
                        raise RuntimeError(f"Failed to fetch PubMed IDs after 3 attempts: {e}")
        return all_ids
    '''
    Method to fetch the papers based on the pubmed_ids and Process in batches to avoid URL-too-long errors
    and Retry up to 3 times and handle the request exception
    '''

    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[Dict[str, Any]]:
        if not pubmed_ids:
            if self.debug:
                print("No PubMed IDs found.")
            return []
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        all_papers: List[Dict[str, Any]] = []
        batch_size = 100  # Process in batches to avoid URL-too-long errors
        for i in range(0, len(pubmed_ids), batch_size):
            batch_ids = pubmed_ids[i:i + batch_size]
            params = {
                "db": "pubmed",
                "id": ",".join(batch_ids),
                "retmode": "xml",
            }
            for attempt in range(3):  # Retry up to 3 times
                try:
                    response = requests.get(base_url, params=params)
                    response.raise_for_status()
                    if self.debug:
                        print(f"Fetching details for PubMed IDs batch: {batch_ids}")
                        print("Response:", response.text)
                    papers = self.parse_paper_details(response.text)
                    all_papers.extend(papers)
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < 2:
                        print(f"Retrying due to error: {e}")
                        time.sleep(2 ** attempt)
                    else:
                        raise RuntimeError(f"Failed to fetch paper details after 3 attempts: {e}")
        return all_papers

    '''
    Method to parse the Paper details based on Output requirements:
     Returntheresults as a CSV file with the following columns:
     PubmedID:Uniqueidentifier for the paper.
     Title: Title of the paper.
     Publication Date: Date the paper was published.
     Non-academicAuthor(s): Names of authors affiliated with non-academic institutions.
     CompanyAffiliation(s): Names of pharmaceutical/biotech companies.
     Corresponding Author Email: Email address of the corresponding author

    And  filter author if  Only  at least one author qualifies (i.e. has a company affiliation)

    '''

    def parse_paper_details(self, xml_data: str) -> List[Dict[str, Any]]:
        papers: List[Dict[str, Any]] = []
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML data: {e}")
        for article in root.findall(".//PubmedArticle"):
            paper = {
                "PubmedID": article.findtext(".//PMID") or "Unknown",
                "Title": article.findtext(".//ArticleTitle") or "Unknown",
                "Publication Date": "",
                "Non-academic Author(s)": "None",
                "Company Affiliation(s)": "None",
                "Corresponding Author Email": "None"
            }
            day = article.findtext(".//PubDate/Day", "")
            month = article.findtext(".//PubDate/Month", "")
            year = article.findtext(".//PubDate/Year", "")
            if day and month and year:
                paper["Publication Date"] = f"{year}/{month}/{day}"
            elif year:
                paper["Publication Date"] = year

            authors: List[str] = []
            affiliations: List[str] = []
            for author in article.findall(".//Author"):
                name = f"{author.findtext('LastName', '')}, {author.findtext('ForeName', '')}"
                affiliation = author.findtext(".//Affiliation", "")
                email = ""
                email_match = re.search(r"[\w.-]+@[\w.-]+", affiliation)
                if email_match:
                    email = email_match.group(0)
                    paper["Corresponding Author Email"] = email
                authors.append(name)
                affiliations.append(affiliation)

            # Filter authors using only company keywords
            non_academic_authors = self.filter_non_academic_authors(authors, affiliations)
            # Only include paper if at least one author qualifies (i.e. has a company affiliation)
            if non_academic_authors:
                paper["Non-academic Author(s)"] = "; ".join(
                    [author["name"] for author in non_academic_authors]
                )
                paper["Company Affiliation(s)"] = "; ".join(
                    [author["company"] for author in non_academic_authors]
                )
                papers.append(paper)
            else:
                if self.debug:
                    print(f"Skipping paper {paper['PubmedID']} as no company affiliation found")
        if self.debug:
            print("Parsed Papers:", papers)
        return papers
    
    '''
        Filter the authors based the non_academic_authors and filter based on 
        Keywords indicating a company affiliation and academic_keywords to 
        Exclude if any academic keyword is present.

    '''

    def filter_non_academic_authors(self, authors: List[str], affiliations: List[str]) -> List[Dict[str, str]]:
        filtered_authors: List[Dict[str, str]] = []
        # Keywords indicating a company affiliation.
        company_keywords = [
            "inc", "ltd", "corp", "corporation", "pharma", "biotech",
            "biopharma", "healthtech", "company", "therapeutics", "healthcare"
        ]
        # Keywords indicating an academic affiliation.
        academic_keywords = [
            "university", "college", "institute", "hospital", "school", "department", "faculty"
        ]
        
        for name, affiliation in zip(authors, affiliations):
            affiliation_lower = affiliation.lower()
            if self.debug:
                print(f"Processing author: {name}, affiliation: {affiliation}")
            
            # Exclude if any academic keyword is present.
            if any(ak in affiliation_lower for ak in academic_keywords):
                if self.debug:
                    print(f"Excluded academic author: {name} with affiliation: {affiliation}")
                continue  # Skip this author
            
            # Include only if any company keyword is present.
            if any(ck in affiliation_lower for ck in company_keywords):
                filtered_authors.append({
                    "name": name,
                    "company": affiliation
                })
                if self.debug:
                    print(f"Included non-academic author: {name} with company affiliation: {affiliation}")
        
        return filtered_authors

    '''
    Method to save the data to csv file using the pandas dataframe
    '''
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str, mode: str = 'w') -> None:
        if not data:
            print("⚠️ No data to save!")
            return
        fieldnames = [
            "PubmedID", "Title", "Publication Date", "Non-academic Author(s)",
            "Company Affiliation(s)", "Corresponding Author Email"
        ]

        # Convert data to a DataFrame using the pandas and Saving DataFrame to CSV
        df = pd.DataFrame(data,columns=fieldnames)
        
        if mode == 'w':
            df.to_csv(filename, index=False, mode='w')
        else:
            df.to_csv(filename, index=False, mode='a', header=False)

        # with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #     if mode == 'w':  # Write header only if file is being created
        #         writer.writeheader()
        #     for row in data:
        #         writer.writerow(row)
