import fitz  # PyMuPDF
import pandas as pd
import os
import logging
import re

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Moves up from src/
LOG_DIR = os.path.join(BASE_DIR, "logs")
RAW_PAPERS_DIR = os.path.join(BASE_DIR, "data/papers")
TABLES_DIR = os.path.join(BASE_DIR, "data/tables")

# Configure logging
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "table_extractor.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Successfully initiated logging")


# Keywords to identify the main results table
RESULTS_KEYWORDS = {"results", "outcome", "findings", "analysis", "efficacy", "impact"}

def extract_text_tables(page_text):
    """ Extracts tables from raw page text using regex-based heuristics. """
    table_regex = re.compile(r"([\w\s\d]+(\t|\s{2,})[\w\s\d]+)+")  # Detects tabular structures
    matches = table_regex.findall(page_text)

    tables = []
    for match in matches:
        rows = match[0].strip().split("\n")  # Split into rows
        structured_table = [re.split(r"\s{2,}|\t", row.strip()) for row in rows if row.strip()]
        tables.append(structured_table)
    
    return tables if tables else None


def is_results_table(table):
    """ Checks if a table is likely to be the main results table. """
    for row in table:
        for cell in row:
            if any(keyword in cell.lower() for keyword in RESULTS_KEYWORDS):
                return True
    return False


def extract_results_table_from_pdf(pdf_path):
    """ Extracts only the main results table from a PDF. """
    try:
        doc = fitz.open(pdf_path)
        candidate_tables = []
        
        for page in doc:
            text = page.get_text("text")  # Extract full page text
            page_tables = extract_text_tables(text)
            if page_tables:
                candidate_tables.extend(page_tables)
        
        if not candidate_tables:
            return None  # No tables found

        # Filter tables to find the most relevant results table
        results_tables = [table for table in candidate_tables if is_results_table(table)]

        if results_tables:
            return max(results_tables, key=len)  # Choose the largest results table
        else:
            return None  # No results-related tables found
    except Exception as e:
        logging.error(f"Error extracting tables from {pdf_path}: {e}")
        return None


def save_table(pubmed_id, table):
    """ Saves the extracted results table to a CSV file. """
    table_df = pd.DataFrame(table)

    if table_df.empty:
        logging.warning(f"Skipping empty results table for {pubmed_id}")
        return

    table_file = os.path.join(TABLES_DIR, f"{pubmed_id}_results_table.csv")
    table_df.to_csv(table_file, index=False, header=False)
    logging.info(f"Results table saved: {table_file}")
    print(f"✅ Results table saved at: {table_file}")


def bulk_extract_results_tables():
    """ Extracts the main results table from all PDFs in the directory. """
    if not os.path.exists(RAW_PAPERS_DIR):
        logging.error(f"Raw papers directory not found: {RAW_PAPERS_DIR}")
        return

    for filename in os.listdir(RAW_PAPERS_DIR):
        if filename.endswith(".pdf"):
            pubmed_id = filename.split(".")[0]
            pdf_path = os.path.join(RAW_PAPERS_DIR, filename)

            logging.info(f"Extracting results table from {filename}")

            results_table = extract_results_table_from_pdf(pdf_path)
            if not results_table:
                logging.warning(f"No results table found in {filename}")
                continue

            save_table(pubmed_id, results_table)


if __name__ == "__main__":
    bulk_extract_results_tables()
