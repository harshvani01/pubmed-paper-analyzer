import os
import requests
import logging
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(filename="logs/downloader.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Directory for storing downloaded PDFs
RAW_PAPERS_DIR = "papers/raw"
URLS_FILE = "pubmed_urls.txt"

def load_urls():
    """ Reads PubMed paper URLs from the file. """
    if not os.path.exists(URLS_FILE):
        logging.error(f"URL file {URLS_FILE} not found!")
        return []
    
    with open(URLS_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    logging.info(f"Loaded {len(urls)} URLs from {URLS_FILE}")
    return urls

def download_paper(pubmed_url: str):
    """ Downloads a paper from the given PubMed URL and saves it to 'papers/raw/'. """
    try:
        filename = os.path.basename(pubmed_url.split("/")[-1]) + ".pdf"
        filepath = os.path.join(RAW_PAPERS_DIR, filename)

        if os.path.exists(filepath):
            logging.info(f"Skipping download. Paper already exists: {filename}")
            return filepath

        logging.info(f"Downloading: {pubmed_url}")
        response = requests.get(pubmed_url, stream=True, timeout=10)

        if response.status_code == 200:
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=4096):
                    f.write(chunk)
            logging.info(f"Download complete: {filename}")
            return filepath
        else:
            logging.error(f"Failed to download {pubmed_url}. HTTP Status: {response.status_code}")
            return None

    except requests.RequestException as e:
        logging.error(f"Error downloading {pubmed_url}: {e}")
        return None

def bulk_download():
    """ Reads URLs from file and downloads multiple papers concurrently. """
    if not os.path.exists(RAW_PAPERS_DIR):
        os.makedirs(RAW_PAPERS_DIR)

    pubmed_urls = load_urls()
    if not pubmed_urls:
        print("No URLs found. Please check pubmed_urls.txt")
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(download_paper, pubmed_urls)

if __name__ == "__main__":
    bulk_download()
