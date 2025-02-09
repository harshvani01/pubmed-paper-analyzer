import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

# PubMed article URL
pubmed_url = "https://pubmed.ncbi.nlm.nih.gov/39368806/"

# Step 1: Get the HTML content of the PubMed page
response = requests.get(pubmed_url, headers={"User-Agent": "Mozilla/5.0"})
if response.status_code != 200:
    print("Failed to fetch the PubMed page")
    exit()

# Step 2: Parse HTML using BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Step 3: Find the Full Text Links Section
full_text_section = soup.find("div", class_="full-text-links")

if not full_text_section:
    print("Full-text links not found.")
    exit()

# Step 4: Extract all full-text links
full_text_links = full_text_section.find_all("a", href=True)

if not full_text_links:
    print("No full-text links found.")
    exit()

links_to_visit = [link["href"] for link in full_text_links]
print(f"Found {len(links_to_visit)} full-text links.")

# Step 5: Setup Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": os.getcwd(),  # Set download directory
    "download.prompt_for_download": False,  # Auto download
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True  # Open PDFs externally
})

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Step 6: Visit each link until successful
pdf_downloaded = False

for redirect_url in links_to_visit:
    print(f"Visiting: {redirect_url}")
    driver.get(redirect_url)
    time.sleep(3)  # Wait for JavaScript to load

    # Step 7: Look for a download button
    download_button = None
    possible_texts = ["Download", "PDF", "Full Text", "Get PDF"]

    for text in possible_texts:
        try:
            download_button = driver.find_element(By.PARTIAL_LINK_TEXT, text)
            if download_button:
                print(f"Found download button: {text}")
                break
        except:
            continue

    if not download_button:
        print("No download button found on this page. Trying next link...")
        continue  # Try the next full-text link

    # Step 8: Click the button instead of fetching href
    try:
        download_button.click()
        print("Clicked the download button, waiting for file to download...")
        time.sleep(5)  # Give time for download

        # Check if the file was downloaded
        downloaded_files = [f for f in os.listdir() if f.endswith(".pdf")]
        if downloaded_files:
            print(f"Downloaded file: {downloaded_files[0]}")
            pdf_downloaded = True
            break  # Stop searching after first successful download

    except Exception as e:
        print(f"Failed to click the button: {e}")

# Cleanup
driver.quit()

if not pdf_downloaded:
    print("No downloadable file found on any of the links.")
