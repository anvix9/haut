import json
import os
import requests
from pathlib import Path
from datetime import datetime 

def get_future_questions(content):
    url = "http://127.0.0.1:11434/api/generate"
    prompt = (
        f"From the Content, Generate two or more research questions that can possibly be practically investigated and studied (be precise) in future experiments by other researchers or the same."
        f"Focus on methodology and the limits that the current document can have to generate the questions. Give the questions as bullets and avoid polite introductory."
        f"Take also in consideration the topics to generate the questions."
        f"Do not give explanations of the questions, just generate them."
        f"Content: {content}"
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

def generate_possible_future_questions(timer):
    # Load paper titles
    with open('paper_metadata/metadata_2024_12_31_143026.json', 'r') as f:
        papers = json.load(f)
    
        # Create output directory
    Path('paper_future_work').mkdir(exist_ok=True)
    output_path = os.path.join('./paper_future_work', f'paper_questions_{timer}.json')
    
    # Initialize or load existing questions
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
    else:
        all_questions = {"questions": []}
    
    # Process each analysis file
    analysis_files = Path('card_papers').glob('*_card.md')
    for analysis_path in analysis_files:
        paper_id = analysis_path.stem.replace('_card', '')
        tag, paper_id = paper_id.split("_")
        
        with open(analysis_path, 'r') as f:
            analysis = f.read()
        
        title = next((paper['title'] for paper in papers if paper['id'] == paper_id), "Unknown Title")
        content = f"{analysis}"
        questions= get_future_questions(content)
        
        if questions:
            questions= questions.split(":")[-1]
            question_entry = {
                "paper_id": paper_id,
                "title": title,
                "questions": questions.strip()
            }
            all_questions["questions"].append(question_entry)
            print(f"Generated questions from {tag}_{paper_id}")
    
    # Save updated questions
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, indent=4)

if __name__ == "__main__":

    # Format it as required: '2020_07_15_143026' (without milliseconds)
    timestamp = datetime.now() 
    formatted_timestamp = timestamp.strftime("%Y_%m_%d_%H%M%S")

    generate_possible_future_questions(formatted_timestamp)


