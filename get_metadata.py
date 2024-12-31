import pandas as pd
import json
import arxiv
import time
import json
import os
from urllib.parse import urlparse
from datetime import datetime 


def fetch_arxiv_data(paper_ids, timestamp):
    data = []
    client = arxiv.Client()
    
    for paper_id in paper_ids:
        tag, paper_id = paper_id.split("_")

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
                "link": paper.entry_id,
                "tag": tag
            }
            data.append(paper_data)
            
            # Download PDF with proper delay
            #pdf_path = f"./data/dair_2023/arxiv_23/{paper_id}.pdf"
            #paper.download_pdf(filename=pdf_path)

            time.sleep(4)  # Respectful delay between requests
            
        except Exception as e:
            print(f"Error processing {paper_id}: {str(e)}")
            
    # Save metadata
    with open(f"./paper_metadata/metadata_{timestamp}.json", 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to metadata_{timestamp}.json")

# Format it as required: '2020_07_15_143026' (without milliseconds)
timestamp = datetime.datetime.now() 
dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
formatted_timestamp = dt.strftime("%Y_%m_%d_%H%M%S")

# Create output directory
# Here I have to make it generic to pass the bucket data
input_folder = "./paper_compressed/"  # Folder containing markdown files
pdf_files = [f.rsplit("_extracted")[0] for f in os.listdir(input_folder) if f.endswith('.md')]

# Use the paper IDs list 
fetch_arxiv_data(pdf_files, formatted_timestamp) 


