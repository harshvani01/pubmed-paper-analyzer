# PubMed Paper Analyzer
A Python-based tool to analyze PubMed papers by extracting summaries and results tables. It includes a REST API to trigger processing.

# 🚀 Features
  📄 Summarization: Extracts and summarizes key information from research papers.
  📊 Results Table Extraction: Identifies and extracts primary results tables from PDFs.
  🔥 Parallel Processing: Uses multi-threading for efficient batch processing.
  🌐 REST API: Simple API to trigger processing and retrieve results.
  
# 📂 Project Structure
pubmed-paper-analyzer/
│── data/                 # Contains raw PDFs and extracted data
│   ├── papers/           # Input PDFs
│   ├── summaries/        # Generated summaries
│   ├── tables/           # Extracted results tables
│── logs/                 # Log files
│── src/                  # Source code
│   ├── summarizer.py     # Extracts and summarizes paper content
│   ├── table_extractor.py# Extracts primary results tables
│   ├── api.py            # REST API to trigger processing
│── main.py               # Orchestrates the entire workflow
│── requirements.txt      # Python dependencies
│── README.md             # Project documentation

# 🔧 Setup
  1️⃣ Install Dependencies
    Create a virtual environment and install required packages:
  
    python -m venv pubmed_analyzer_env
    source pubmed_analyzer_env/bin/activate  # (Linux/macOS)
    pubmed_analyzer_env\Scripts\activate     # (Windows)

    pip install -r requirements.txt
    
# 📊 Usage
  Run the analysis manually:
    -> add the desired paper URLs in the input_urls.txt and then the below command.
    python main.py
  Run the REST API:
    uvicorn src.api:app --host 0.0.0.0 --port 8000
  API Endpoints:
  Method	 Endpoint 	Description
  GET	        /	      API health check
  POST	   /analyze	  Triggers main.py processing
  GET      /summary/{pubmed_id}   get the summary of a paper based on pubmed id.
  GET      /table/{pubmed_id}     get result table of the paper based on the pubmed id.
  
# 📝 Logs & Outputs
  Summaries: data/summaries/
  Tables: data/tables/
  Logs: logs/
  
# 🛠️ Troubleshooting
  1️⃣ No summaries/tables generated?
  
  Check logs/ for errors.
  Ensure data/papers/ has valid PDFs.
  2️⃣ API not responding?

  Ensure uvicorn is running (http://127.0.0.1:8000).
  
# 📜 License
  This project is for educational purposes. Feel free to modify and extend!

# Sample
  You can find the Sample/ directory which contains the sample papers and their summary and tables extracted.

# PubMed Paper Analyzer - Key Highlights
PDF Summarization:
  Extracts text from research papers using PyMuPDF.
  Splits text into chunks and summarizes them using Hugging Face’s BART-Large model.
  Stores summaries in structured text files inside the data/summaries/ directory.
Results Table Extraction:
  Identifies and extracts the primary results table from each PDF.
  Converts tables into structured CSV format for easy analysis.
Logging & Robust Error Handling:
  Comprehensive logging system tracks processing steps and errors.
  Handles edge cases such as empty PDFs, missing text, and malformed tables.
Parallel Processing for Efficiency:
  Uses ThreadPoolExecutor to process multiple papers in parallel.
  Improves performance when handling large batches of PDFs.
RESTful API for Automation:
  Simple Flask-based API to trigger the analysis process.
  Provides endpoints to retrieve summaries and tables for specific papers.
Well-Structured Codebase:
  Organized into src/ for main logic and data/ for processed outputs.
  Uses configurable directory paths to ensure proper file organization.
  
This implementation efficiently extracts and summarizes research findings while maintaining scalability, automation, and structured data storage. 🚀


