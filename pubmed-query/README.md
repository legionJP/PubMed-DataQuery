#
# Fetchpapersusing the PubMed AP

# 1. Program Setup 

# Queries : 

### Query for results1
poetry run get-papers-list "non-small cell lung cancer AND (Pfizer OR Roche OR Novartis) AND (immunotherapy OR targeted therapy) AND 2023[dp]" -f pubmed_results4.csv -d

### Query for the pubmed_result4.csv
- It is matching about the 7105+ results and saving 1K+ results according to requiements
poetry run get-papers-list "cardiovascular disease AND (therapeutics OR treatment) AND (pharma OR pharmaceutical OR biotech) AND 2023[dp]" -f pubmed_results4.csv -d


# Usages Guide: 

# 1.  Basic Query
poetry run get-papers-list "lung cancer AND (targeted therapy OR immunotherapy) AND (pharma OR pharmaceutical OR biotech) AND 2023[dp]"


# 2. Specifying the Output file by -f 
poetry run get-papers-list "lung cancer AND (targeted therapy OR immunotherapy) AND (pharma OR pharmaceutical OR biotech) AND 2023[dp]" -f lung_cancer_results.csv

# 3. Specifying Output File and Enabling Debug Mode
- prints the debug info

poetry run get-papers-list "lung cancer AND (targeted therapy OR immunotherapy) AND (pharma OR pharmaceutical OR biotech) AND 2023[dp]" -f lung_cancer_results.csv -d


# Display Usage Instructions:
```
argparse Automatically Includes -h or --help: The argparse module automatically includes a -h or --help option that displays the usage instructions. When you run your script with the -h flag, argparse will print the help message and exit.
```
- poetry run get-papers-list -h

# Query Syntax:

AND: Combines different keywords to narrow down the search.

OR: Includes any of the listed terms in the search.

[dp]: Stands for "Date of Publication," which limits the search to papers published in the specified year



# Publishing the Package to Pypi

Upload to Test PyPI (optional, for testing):

```bash
poetry config repositories.test-pypi https://test.pypi.org/legacy/
poetry publish -r test-pypi
```

Upload to PyPI:
```bash
poetry publish --username __token__ --password <your-pypi-token>
```