import requests
from bs4 import BeautifulSoup
import os
import json
import re
from time import sleep

def get_paper_title(paper_id):
    url = f"https://arxiv.org/abs/{paper_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_element = soup.find('h1', class_='title mathjax')
        if title_element:
            # Remove 'Title:' prefix and clean up whitespace
            title = title_element.text.replace('Title:', '').strip()
            return title
        return None
    except Exception as e:
        print(f"Error fetching title for {paper_id}: {str(e)}")
        return None

def scrape_titles(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    titles_dict = {}
    
    md_files = [f for f in os.listdir(input_folder) if f.endswith('.md')]
    
    for md_file in md_files:
        # Extract paper ID (remove .md extension)
        paper_id = os.path.splitext(md_file)[0]
        print(f"Fetching title for {paper_id}")
        
        title = get_paper_title(paper_id)
        if title:
            titles_dict[paper_id] = title
        
        # Be nice to ArXiv servers
        sleep(1)
    
    # Save titles to JSON
    output_path = os.path.join(output_folder, 'paper_titles.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(titles_dict, f, indent=4)
    
    return titles_dict

if __name__ == "__main__":
    input_folder = "./converted_markdown_trends"
    output_folder = "./paper_title_metadata"
    titles = scrape_titles(input_folder, output_folder)
