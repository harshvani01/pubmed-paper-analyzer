from fastapi import FastAPI, HTTPException
import os
import subprocess
import logging

# Define directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMARIES_DIR = os.path.join(BASE_DIR, "data/summaries")
TABLES_DIR = os.path.join(BASE_DIR, "data/tables")

# Configure logging
LOG_FILE = os.path.join(LOG_DIR, "api.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "PubMed Paper Analyzer API is running!"}


@app.post("/analyze")
def trigger_analysis():
    """Trigger the main analysis process (main.py)."""
    try:
        logging.info("Received request to trigger analysis.")
        
        # Run main.py as a subprocess
        process = subprocess.Popen(["python", os.path.join(BASE_DIR, "main.py")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logging.error(f"Analysis process failed: {stderr.decode()}")
            raise HTTPException(status_code=500, detail="Failed to execute analysis script.")
        
        logging.info("Analysis process completed successfully.")
        return {"message": "Analysis started successfully"}
    
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/summary/{pubmed_id}")
def get_summary(pubmed_id: str):
    """ Retrieve the summary of a specific paper. """
    summary_path = os.path.join(SUMMARIES_DIR, f"{pubmed_id}_summary.txt")

    if not os.path.exists(summary_path):
        raise HTTPException(status_code=404, detail="Summary not found")

    with open(summary_path, "r") as file:
        summary = file.read()

    return {"pubmed_id": pubmed_id, "summary": summary}


@app.get("/table/{pubmed_id}")
def get_table(pubmed_id: str):
    """ Retrieve the extracted results table of a specific paper. """
    table_path = os.path.join(TABLES_DIR, f"{pubmed_id}_results_table.csv")

    if not os.path.exists(table_path):
        raise HTTPException(status_code=404, detail="Results table not found")

    with open(table_path, "r") as file:
        table_data = file.readlines()

    return {"pubmed_id": pubmed_id, "table": table_data}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
