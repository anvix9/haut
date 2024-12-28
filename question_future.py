import json
import os
import requests
from pathlib import Path

def get_gemma_summary(content):
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

def generate_possible_future_questions():
    # Load paper titles
    with open('paper_metadata/paper_titles.json', 'r') as f:
        titles = json.load(f)
    
    # Create output directory
    Path('paper_future_work').mkdir(exist_ok=True)
    output_path = os.path.join('./paper_future_work', 'paper_questions.json')
    
    # Initialize or load existing questions
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
    else:
        all_questions = {"questions": []}
    
    # Process each analysis file
    analysis_files = Path('paper_cards').glob('*_card.md')
    for analysis_path in analysis_files:
        paper_id = analysis_path.stem.replace('_card', '')
        
        with open(analysis_path, 'r') as f:
            analysis = f.read()
        
        title = titles.get(paper_id, "Unknown Title")
        content = f"{analysis}"
        summary = get_gemma_summary(content)
        
        if summary:
            summary = summary.split(":")[-1]
            question_entry = {
                "paper_id": paper_id,
                "title": title,
                "questions": summary.strip()
            }
            all_questions["questions"].append(question_entry)
            print(f"Generated questions from {paper_id}")
    
    # Save updated questions
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, indent=4)

if __name__ == "__main__":
    generate_possible_future_questions()
