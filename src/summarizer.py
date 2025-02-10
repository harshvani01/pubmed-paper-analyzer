import fitz  # PyMuPDF
import os
import logging
from transformers import pipeline
from concurrent.futures import ThreadPoolExecutor

# Configure logging
# Get the directory where this script is located
# Get the absolute path of the project's root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Moves up from src/
LOG_DIR = os.path.join(BASE_DIR, "logs")  # Ensure logs stay inside project
SUMMARIES_DIR = os.path.join(BASE_DIR, "data/summaries")  # Ensure summaries stay inside project
# Directories
RAW_PAPERS_DIR = os.path.join(BASE_DIR, "data/papers")
CHUNK_SIZE = 500


# Ensure directories exist
os.makedirs(SUMMARIES_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RAW_PAPERS_DIR, exist_ok=True)

# Configure logging
import logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "summarizer.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Successfully initiated logging")

# Initialize summarization pipeline
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    logging.error(f"Failed to initialize summarizer: {e}")
    raise SystemExit("Error: Summarization pipeline failed to load.")

def extract_text_from_pdf(pdf_path, chunk_size=CHUNK_SIZE):
    try:
        doc = fitz.open(pdf_path)

        text = " ".join([page.get_text().strip() for page in doc if page.get_text().strip()])

        if not text:
            logging.error(f"PDF {pdf_path} contains no extractable text.")
            return None

        words = text.split()
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        return [chunk for chunk in chunks if len(chunk.split()) >= 50]
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return None



def summarize_text_chunks(chunks, max_length=250):
    summaries = []
    for i, chunk in enumerate(chunks):
        try:
            if len(chunk.split()) < 50:
                logging.warning(f"Skipping short chunk ({len(chunk.split())} words).")
                continue

            chunk = " ".join(chunk.split()[:CHUNK_SIZE])  # Limit chunk size
            summary = summarizer(chunk, max_length=max_length, min_length=30, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        except Exception as e:
            logging.error(f"Error summarizing text chunk {i}: {e}")
    return " ".join(summaries) if summaries else None

def summarize_paper(pdf_path):
    """ Summarizes a paper given its PDF path. """
    pubmed_id = os.path.basename(pdf_path).replace(".pdf", "")
    summary_path = os.path.join(SUMMARIES_DIR, f"{pubmed_id}_summary.txt")

    if os.path.exists(summary_path):
        logging.info(f"Skipping {pubmed_id}, summary already exists.")
        return

    logging.info(f"Summarizing: {pdf_path}")

    text_chunks = extract_text_from_pdf(pdf_path)
    if not text_chunks:
        logging.error(f"No valid text extracted from {pdf_path}, skipping.")
        return
    
    summary = summarize_text_chunks(text_chunks)
    if not summary:
        logging.error(f"Failed to generate summary for {pdf_path}, skipping.")
        return
    
    with open(summary_path, "w") as f:
        f.write(summary)

    logging.info(f"Summary saved: {summary_path}")



def bulk_summarize():
    """ Summarizes all papers in parallel. """
    pdf_files = [os.path.join(RAW_PAPERS_DIR, f) for f in os.listdir(RAW_PAPERS_DIR) if f.endswith(".pdf")]
    
    if not pdf_files:
        logging.error(f"No PDFs found in {RAW_PAPERS_DIR}.")
        return
    
    MAX_THREADS = 3
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(summarize_paper, pdf_files)

    logging.info("Bulk summarization completed.")


if __name__ == "__main__":
   #  summarize_paper("/Users/hvani/personal/project/pubmed-paper-analyzer/data/papers/39368806.pdf")
    bulk_summarize()
