import argparse # command line parsing lib
from pubmed_fetcher.pubmed_fetcher  import PubMedFetcher

class GetPapersList:
    def __init__(self) -> None:
        self.pubmed_fetcher = PubMedFetcher()
  
    def run(self) -> None:
        ''''
        Function to parse the command line arguments
        '''      

        parser = argparse.ArgumentParser(description='Fetch papers from PubMed and save to CSV.')
        parser.add_argument('query', type=str, help='PubMed query')
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


# import argparse  # Command line parsing library
# from pubmed_fetcher.pubmed_fetcher import PubMedFetcher

# class GetPapersList:
#     def __init__(self):
#         self.pubmed_fetcher = PubMedFetcher()

#     def run(self):
#         """
#         Function to parse the command line arguments and execute the program.
#         """
#         parser = argparse.ArgumentParser(description='Fetch papers from PubMed and save to CSV.')
#         parser.add_argument('query', type=str, help='PubMed query')
#         parser.add_argument('-f', '--file', type=str, help='Output CSV file name')
#         parser.add_argument('-d', '--debug', action='store_true', help='Print debug information')
#         args = parser.parse_args()

#         if args.debug:
#             print(f'Query: {args.query}')
#             if args.file:
#                 print(f'Output file: {args.file}')

#         try:
#             # Fetch PubMed IDs
#             pubmed_ids = self.pubmed_fetcher.fetch_pubmed_ids(args.query)
            
#             # Post IDs to Entrez History Server
#             webenv, query_key = self.pubmed_fetcher.post_ids_to_history(pubmed_ids)
            
#             # Fetch Paper Details from History Server
#             retstart = 0
#             retmax = 200
#             all_details = []
            
#             while True:
#                 details_batch = self.pubmed_fetcher.fetch_paper_details_from_history(webenv, query_key, retstart, retmax)
#                 if not details_batch:
#                     break
#                 all_details.extend(details_batch)
#                 retstart += retmax

#             # Save data to CSV if file name is provided, else print to console
#             if args.file:
#                 self.pubmed_fetcher.save_to_csv(all_details, args.file)
#             else:
#                 for row in all_details:
#                     print(row)

#         except Exception as e:
#             print(f"Error occurred: {e}")

# def run():
#     GetPapersList().run()

# if __name__ == '__main__':
#     run()
