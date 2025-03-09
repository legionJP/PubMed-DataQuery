import argparse # command line parsing lib
from pubmed_fetcher.pubmed_fetcher  import PubMedFetcher

class GetPapersList:
    def __init__(self) -> None:
        self.pubmed_fetcher = PubMedFetcher()
  
    def run(self) -> None:
        ''''
        Function to parse the command line arguments using the ArgumentParser
        '''      

        parser = argparse.ArgumentParser(description='Fetch papers from PubMed and save to CSV file.')
        parser.add_argument('query', type=str, help='PubMed query Syntax: Example- "keyword AND (keyword2 OR keyword3) AND (keyword4 OR keyword5) AND 2023[dp]"')
        parser.add_argument('-f', '--file', type=str, help='Output CSV File name')
        parser.add_argument('-d', '--debug', action='store_true',help='Print debug information')
        args = parser.parse_args()

        self.pubmed_fetcher.debug = args.debug

        if args.debug:
            print(f'Query:{args.query}')
            if args.file:
                print(f'output file: {args.file}')
        
        try:
            pubmed_ids = self.pubmed_fetcher.fetch_pubmed_ids(args.query)
            data = self.pubmed_fetcher.fetch_paper_details(pubmed_ids)

            if args.file:
                self.pubmed_fetcher.save_to_csv(data,args.file)
            else:
                if data:
                    for row in data:
                        print(row)
                else:
                    print("No Matching papers found")
        except Exception as e:
            print(f"Error occured: {e}")

def run() -> None:
    GetPapersList().run()    
        
if __name__ == '__main__':
    run()
