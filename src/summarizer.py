import fitz  # PyMuPDF
from transformers import pipeline
import os
import logging

# Configure logging
logging.basicConfig(filename="../logs/summarizer.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Directories
RAW_PAPERS_DIR = "../data/papers"
SUMMARIES_DIR = "../data/summaries"

# Initialize summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text_from_pdf(pdf_path):
    """ Extracts text from a PDF file. """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return None

def summarize_text(text, max_length=250):
    """ Generates a summary of the given text. """
    try:
        # Truncate text to fit within the model's token limit
        truncated_text = " ".join(text.split()[:1000])
        summary = summarizer(truncated_text, max_length=max_length, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        logging.error(f"Error summarizing text: {e}")
        return None

def summarize_paper(pdf_path):
    """ Summarizes a paper given its PDF path. """
    if not os.path.exists(pdf_path):
        logging.error(f"PDF file not found: {pdf_path}")
        return None

    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text:
        logging.error(f"No text extracted from {pdf_path}")
        return None

    # Generate summary
    summary = summarize_text(text)
    if not summary:
        logging.error(f"Failed to generate summary for {pdf_path}")
        return None

    return summary

def save_summary(pubmed_id, summary):
    """ Saves the summary to a file. """
    if not os.path.exists(SUMMARIES_DIR):
        os.makedirs(SUMMARIES_DIR)

    summary_file = os.path.join(SUMMARIES_DIR, f"{pubmed_id}_summary.txt")
    with open(summary_file, "w") as f:
        f.write(summary)
    logging.info(f"Summary saved: {summary_file}")

def bulk_summarize():
    """ Summarizes all papers in the raw papers directory. """
    if not os.path.exists(RAW_PAPERS_DIR):
        logging.error(f"Raw papers directory not found: {RAW_PAPERS_DIR}")
        return

    for filename in os.listdir(RAW_PAPERS_DIR):
        if filename.endswith(".pdf"):
            pubmed_id = filename.split(".")[0]  # Extract PubMed ID from filename
            pdf_path = os.path.join(RAW_PAPERS_DIR, filename)

            # Summarize the paper
            summary = summarize_paper(pdf_path)
            if not summary:
                logging.error(f"Skipping {filename}: Failed to generate summary")
                continue

            # Save the summary
            save_summary(pubmed_id, summary)

if __name__ == "__main__":
    bulk_summarize()