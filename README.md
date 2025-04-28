#
# PubMed Research Paper Fetcher

## Description

#### Fetch Papers Using The PubMed API
This Python program fetches research papers from PubMed based on a user-specified query. It identifies papers with at least one author affiliated with a pharmaceutical or biotech company and returns the results as a CSV file.

# Project Organization

- ## [Module: pubmed_fetcher.py](pubmed-query/pubmed_fetcher/pubmed_fetcher.py)
- ## Installing and setting-up program [Installation and Setup](/#Installation and Setup)
- ## 

  ## Features: 
- modular functions and classe Concept
- Fetches papers using the PubMed API.
- Supports PubMed's full query syntax for flexibility.
- Filter non-academic authors based on their affiliations.
- Returns results with the following columns and save in CSV file:
  - **PubmedID**: Unique identifier for the paper.
  - **Title**: Title of the paper.
  - **Publication Date**: Date the paper was published.
  - **Non-academic Author(s)**: Names of authors affiliated with non-academic institutions.
  - **Company Affiliation(s)**: Names of pharmaceutical/biotech companies.
  - **Corresponding Author Email**: Email address of the corresponding author.

- ## [Module: get_paper_list.py](/pubmed-query/get_paper_list/get_paper_list.py)

- Features
- This module's script is the entry point of the application. It has run method to parse the command line arguments using the ArgumentParser
- Command-line options:
  - **-h or --help**: Display usage instructions.
  - **-d or --debug**: Print debug information during execution.
  - **-f or --file**: Specify the filename to save the results. If this option is not provided, print the output to the console.

- ### Command line Instructions:

- argparse Automatically Includes -h or --help: The argparse module automatically includes a -h or --help option that displays the usage instructions. 
```
  poetry run get-papers-list -h
```
- ## Query Syntax:

AND: Combines different keywords to narrow down the search.
OR: Includes any of the listed terms in the search.
[dp]: Stands for "Date of Publication," which limits the search to papers published in the specified year


# Code Structure 

```py
# Module: pubmed_fetcher.py
# PubMedFetcher Class

__init__(self, debug: bool = False) -> None: Initializes the fetcher with optional debug mode.

fetch_pubmed_ids(self, query: str) -> List[str]: Fetches PubMed IDs based on the query.

fetch_paper_details(self, pubmed_ids: List[str]) -> List[Dict[str, Any]]: Fetches paper details for given PubMed IDs.

parse_paper_details(self, xml_data: str) -> List[Dict[str, Any]]: Parses XML data to extract paper details.
filter_non_academic_authors(self, authors: List[str], affiliations: List[str]) -> List[Dict[str, str]]: Filters non-academic authors based on company keywords.
save_to_csv(self, data: List[Dict[str, Any]], filename: str, mode: str = 'w') -> None: Saves data to a CSV file using pandas.
Command-line Program: get_paper_list.py
GetPapersList Class
__init__(self) -> None: Initializes the command-line interface.
run(self) -> None: Parses command-line arguments and executes the program logic.
Function: run() -> None: Executes the GetPapersList class.
```
# Installation and Setup

### Prerequisites
- Python 3.12 or higher
- Poetry for dependency management

## Steps for Installtion , Setup
### - 1. Clone Repository : 
   -  git clone https://github.com/legionJP/PubMed-DataQuery 

### -2. Install Python and Poetry
    - curl -sSL https://install.python-poetry.org | python3 
    -(If pip isn't installed install it form pypi)
    - pip install poetry
### 3. Poetry Project Setup 
    - poetry init
    - poetry install
    - poetry add requests [module]
    - poetry shell 
    - poetry run [main-module]

# Program Execution Steps :
Program follows all the Query Syntax from the pubmed API see the reference link : [PubMed API](https://www.ncbi.nlm.nih.gov/books/NBK25497/#chapter2.Usage_Guidelines_and_Requiremen)

- Query Execution Examples 
- ### 1. Basic Query

```bash
poetry run get-papers-list "lung cancer AND (targeted therapy OR immunotherapy) AND (pharma OR pharmaceutical OR biotech) AND 2023[dp]"
```
- ### 2. Specifying Output CSV File Name

```bash
poetry run get-papers-list "lung cancer AND (targeted therapy OR immunotherapy) AND (pharma OR pharmaceutical OR biotech) AND 2023[dp]" -f lung_cancer_results.csv
```
- ### 3. Enabling/Using Debug Mode

```bash
poetry run get-papers-list "lung cancer AND (targeted therapy OR immunotherapy) AND (pharma OR pharmaceutical OR biotech) AND 2023[dp]" -d
```
- ### 4. Specifying Output File and Enabling Debug Mode

```bash
poetry run get-papers-list "lung cancer AND (targeted therapy OR immunotherapy) AND (pharma OR pharmaceutical OR biotech) AND 2023[dp]" -f lung_cancer_results.csv -d
```

# Tools Used

- ## Python Libraries:

    - requests: For making HTTP requests to the PubMed API.
    - pandas: For data manipulation and saving results to CSV.
    - argparse: For parsing command-line arguments.
    - xml.etree.ElementTree: For parsing XML data from the PubMed API.
- ## Development Tools:
    - [Poetry](https://python-poetry.org/docs/)    : for Dependecy Management and Packaging
    - [pytest](https://docs.pytest.org/en/stable/) : to write and running the test cases
    
- ## LLM Assistance: 
    - Project was developed with the assistance from Open-AI ChatGPT4 by using the right prompts
    - Code Refactoring and readibility, Error Handling
    - [Open AI ChatGPT4](https://chatgpt.com/share/67ce4517-b6c4-8012-9db2-42090ff54487)


# Publish the module in test-pypi.

# Publishing Steps
- Configure pyproject.toml is correctly
- Use Poetry to build and publish:

# Command to Publish on Pypi
```bash
poetry build
poetry config repositories.test-pypi https://test.pypi.org/legacy/
poetry publish -r test-pypi

# OR
poetry publish --username __token__ --password <your-pypi-token>
```

### Install Package from PyPi 
- pip install -i [Module on pypi](https://test.pypi.org/...)

### License 
- This project is licensed under MIT License see [LICENSE](/LICENSE)
