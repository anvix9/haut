import pandas as pd
import json
import arxiv
import time
import json
import os
from urllib.parse import urlparse

def fetch_arxiv_data(paper_ids):
    data = []
    client = arxiv.Client()
    
    for paper_id in paper_ids:
        print(f"Fetching {paper_id}...")
        try:
            # Use the official API to search
            search = arxiv.Search(id_list=[paper_id])
            paper = next(client.results(search))
            
            # Extract data
            paper_data = {
                "id": paper_id,
                "title": paper.title,
                "authors": [str(author) for author in paper.authors],
                "submission_date": paper.published.strftime("%Y-%m-%d"),
                "link": paper.entry_id
            }
            data.append(paper_data)
            
            # Download PDF with proper delay
            pdf_path = f"./data/dair_2023/arxiv_23/{paper_id}.pdf"
            paper.download_pdf(filename=pdf_path)

            time.sleep(4)  # Respectful delay between requests
            
        except Exception as e:
            print(f"Error processing {paper_id}: {str(e)}")
            
    # Save metadata
    with open("./paper_metadata/arxiv_data.json", 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print("Data saved to arxiv_data.json")

# Create output directory
output_folder = "./data/dair_2023/arxiv_23"
os.makedirs(output_folder, exist_ok=True)

dair= pd.read_csv("./data/dair_2023.csv")
list_paper_ids = []

for p in dair["dair_2023"]:
    tmp_p = p.rsplit("/",1)[-1]
    list_paper_ids.append(tmp_p)
# Example usage

# Create a directory to save PDFs
output_folder = "./data/dair_2023/arxivfs"
os.makedirs(output_folder, exist_ok=True)

# Use the same paper IDs list you already have
fetch_arxiv_data(list_paper_ids)#Dair_data

