import argparse # command line parsing lib
from pubmed_fetcher.pubmed_fetcher  import PubmedFetcher

class GetPapersList:
    def __init__(self):
        self.pubmed_fetcher = PubmedFetcher()
  
    def run(self):
        ''''
        Function to parse the command line arguments
        '''      

        parser = argparse.ArgumentParser(description='Fetch papers from PubMed and save to CSV.')
        parser.add_argument('query', type=str, help='PubMed query')
        parser.add_argument('-f', '--file', type=str, help='Output CSV File name')
        parser.add_argument('-d', '--debug', action='store_true',help='Print debug information')
        args = parser.parse_args()

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
                for row in data:
                    print(row)
        except Exception as e:
            print(f"Error occured: {e}")

def run():
    GetPapersList().run()    
        
if __name__ == '__main__':
    run()