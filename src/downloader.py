import os
import time
import logging
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
LOG_DIR = "../logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "downloader.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Directories
RAW_PAPERS_DIR = "../data/papers"
URLS_FILE = "../input_urls.txt"

# Ensure directories exist
os.makedirs(RAW_PAPERS_DIR, exist_ok=True)

def load_urls():
    """ Reads PubMed URLs from the file. """
    if not os.path.exists(URLS_FILE):
        logging.error(f"URL file {URLS_FILE} not found!")
        return []
    
    with open(URLS_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    logging.info(f"Loaded {len(urls)} URLs from {URLS_FILE}")
    return urls

def fetch_full_text_links(pubmed_url):
    """ Extracts all full-text links from a PubMed article page. """
    logging.info(f"Fetching full-text links from {pubmed_url}")

    response = requests.get(pubmed_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        logging.error(f"Failed to fetch {pubmed_url}, status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    full_text_section = soup.find("div", class_="full-text-links")

    if not full_text_section:
        logging.warning(f"No full-text links found on {pubmed_url}")
        return []

    links = [link["href"] for link in full_text_section.find_all("a", href=True)]
    logging.info(f"Found {len(links)} full-text links on {pubmed_url}")
    return links

def setup_selenium():
    """ Sets up the Selenium WebDriver in headless mode. """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    })

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def download_pdf(driver, redirect_url, paper_id):
    """ Attempts to find and download a PDF from the given page. """
    logging.info(f"Visiting: {redirect_url}")
    driver.get(redirect_url)
    time.sleep(3)  # Wait for JavaScript to load

    download_button = None
    possible_texts = ["Download", "PDF", "Full Text", "Get PDF"]

    for text in possible_texts:
        try:
            download_button = driver.find_element(By.PARTIAL_LINK_TEXT, text)
            if download_button:
                logging.info(f"Found download button labeled '{text}' on {redirect_url}")
                break
        except:
            continue

    if not download_button:
        logging.warning(f"No download button found on {redirect_url}")
        return None

    # Click the button and wait for the file to download
    try:
        download_button.click()
        logging.info("Clicked the download button, waiting for file to download...")
        time.sleep(5)  # Give time for download

        # Check if a PDF was downloaded
        downloaded_files = [f for f in os.listdir() if f.endswith(".pdf")]
        if downloaded_files:
            filename = os.path.join(RAW_PAPERS_DIR, f"{paper_id}.pdf")
            os.rename(downloaded_files[0], filename)
            logging.info(f"Successfully downloaded: {filename}")
            return filename

    except Exception as e:
        logging.error(f"Error clicking download button: {e}")

    return None

def process_pubmed_url(pubmed_url):
    """ Processes a single PubMed URL: extracts full-text links, attempts to download the PDF. """
    paper_id = pubmed_url.split("/")[-2]  # Extracts the PubMed ID
    pdf_path = os.path.join(RAW_PAPERS_DIR, f"{paper_id}.pdf")

    # Skip if already downloaded
    if os.path.exists(pdf_path):
        logging.info(f"Skipping {pubmed_url}, already downloaded: {pdf_path}")
        return

    logging.info(f"Processing PubMed URL: {pubmed_url}")
    full_text_links = fetch_full_text_links(pubmed_url)
    
    if not full_text_links:
        logging.warning(f"No full-text links found for {pubmed_url}, skipping.")
        return

    driver = setup_selenium()
    pdf_downloaded = False

    for link in full_text_links:
        if download_pdf(driver, link, paper_id):
            pdf_downloaded = True
            break  # Stop after first successful download

    driver.quit()

    if not pdf_downloaded:
        logging.error(f"Failed to download any PDF for {pubmed_url}")

def downloader_logic():
    urls = load_urls()
    if not urls:
        logging.error("No URLs found, exiting.")
        return

    MAX_THREADS = 3  # Control the number of parallel downloads
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(process_pubmed_url, urls)

    logging.info("Process completed.")

if __name__ == "__main__":
    downloader_logic()
