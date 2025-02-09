import fitz  # PyMuPDF
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(filename="../logs/table_extractor.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Directories
RAW_PAPERS_DIR = "../data/papers"
TABLES_DIR = "../data/tables"

def extract_tables_from_pdf(pdf_path):
    """ Extracts tables from a PDF file. """
    try:
        doc = fitz.open(pdf_path)
        tables = []
        for page in doc:
            tables.extend(page.get_tables())
        return tables
    except Exception as e:
        logging.error(f"Error extracting tables from {pdf_path}: {e}")
        return None

def save_table(pubmed_id, table, index):
    """ Saves the table to a CSV file. """
    if not os.path.exists(TABLES_DIR):
        os.makedirs(TABLES_DIR)

    table_file = os.path.join(TABLES_DIR, f"{pubmed_id}_table_{index}.csv")
    table.to_csv(table_file, index=False)
    logging.info(f"Table saved: {table_file}")

def bulk_extract_tables():
    """ Extracts tables from all papers in the raw papers directory. """
    if not os.path.exists(RAW_PAPERS_DIR):
        logging.error(f"Raw papers directory not found: {RAW_PAPERS_DIR}")
        return

    for filename in os.listdir(RAW_PAPERS_DIR):
        if filename.endswith(".pdf"):
            pubmed_id = filename.split(".")[0]  # Extract PubMed ID from filename
            pdf_path = os.path.join(RAW_PAPERS_DIR, filename)

            # Extract tables from PDF
            tables = extract_tables_from_pdf(pdf_path)
            if not tables:
                logging.error(f"No tables found in {filename}")
                continue

            # Save each table
            for i, table in enumerate(tables):
                df = pd.DataFrame(table)
                save_table(pubmed_id, df, i)

if __name__ == "__main__":
    bulk_extract_tables()