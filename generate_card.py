import json
import os
import requests
from pathlib import Path

def get_gemma_summary(content):
    url = "http://127.0.0.1:11434/api/generate"
    prompt = (
        f"Summarize this paper content into a bulleted list of main results, Methods and contributions. Just give the answer without any polite texts before."
        f"Be short and concise no more than 700 characters."
        f"Focus on key findings and avoid technical details and add the key words from the topics at the end. Content: {content}"
    )
    
    payload = {
        "model": "saish_15/tethysai_research",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.json()['response']
    except Exception as e:
        print(f"Error getting summary: {e}")
        return None

def generate_paper_cards():
    # Load paper titles
    with open('paper_metadata/paper_titles.json', 'r') as f:
        titles = json.load(f)
    
    # Create output directory
    Path('paper_cards').mkdir(exist_ok=True)
    
    # Process each analysis file
    analysis_files = Path('paper_analysis').glob('*_analysis.json')
    for analysis_path in analysis_files:
        paper_id = analysis_path.stem.replace('_analysis', '')
        
        with open(analysis_path, 'r') as f:
            analysis = json.load(f)
        
        # Get paper title
        title = titles.get(paper_id, "Unknown Title")
        
        # Combine content for summary
        content = f"{analysis['topics']}\n{analysis['research']}\n{analysis['method']}\n{analysis['results']}"
        summary = get_gemma_summary(content)
        summary = summary.split(":")[-1]
        
        tmp_topics = ", ".join(analysis['topics'])
        # Generate markdown content
        md_content = f"""# {title}

# Research questions
{analysis['research']}

## Problem Statement, Methods and Main Results
{summary}

#### Keywords: {tmp_topics}\n

### [Link to paper](https://arxiv.org/abs/{paper_id})
"""
        
        # Save to markdown file
        output_path = f"paper_cards/{paper_id}_card.md"
        with open(output_path, 'w') as f:
            f.write(md_content)
        
        print(f"Generated card for {paper_id}")

if __name__ == "__main__":
    generate_paper_cards()
