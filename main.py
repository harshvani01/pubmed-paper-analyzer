from src.downloader import bulk_download
from src.summarizer import bulk_summarize
from src.table_extractor import bulk_extract_results_tables

def main():
    print("Starting PubMed Paper Analyzer...")
    bulk_download()
    bulk_summarize()
    bulk_extract_results_tables()
    print("Analysis complete!")

if __name__ == "__main__":
    main()