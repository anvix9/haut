import requests
from pathlib import Path
import re 
import os
import json 
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from typing import Dict, List, Union
from tqdm import tqdm
from dotenv import load_dotenv

## Load Current folder 
def load_json_files(directory='./paper_cards/'):
    """
    Load all JSON files from the specified directory.
    Args:
        directory (str): Path to the directory containing JSON files. Defaults to current directory.
    Returns:
        dict: Dictionary with filenames as keys and JSON content as values
    """
    json_files = {}
    
    # Get all JSON files in the directory
    for file_path in Path(directory).glob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Load JSON content
                md_content = file.read() 
                # Use filename as key
                json_files[file_path.name] = md_content
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return json_files

def extract_questions_and_filename(source, text):
    # Extract filename without '_analysis.json'
    filename = source.replace('_card.md', '')
    
    return text, filename


## Index card_papers 

def get_embeddings(content: str) -> List[float]:
    """Get embeddings from tethysai_research model via Ollama"""
    _url = "http://127.0.0.1:11434/api/embed"
    
    _payload = {
        "model": "saish_15/tethysai_research",
        "input": f"Content: {content}"
    }
    
    try:
        response = requests.post(_url, json=_payload)
        response.raise_for_status()
        return response.json()['embeddings']
    except Exception as e:
        print(f"Error extracting embedding: {str(e)}")
        return None


def upsert_to_pinecone(index, data: Dict[str, List[str]]) -> None:
    """Upsert embeddings and metadata to Pinecone"""
    batch_size = 100
    vectors_batch = []
    
    for paper_id, card in tqdm(data.items(), desc="Processing card papers"):
        #for i, question in enumerate(card):
        embedding = get_embeddings(card)
        if embedding:
            vector = {
                'id': f"{paper_id}",
                'values': embedding[0],
                'metadata': {
                    'paper_id': paper_id,
                    'question': card,
                    #'question_number': i
                }
            }
            vectors_batch.append(vector)
            
            # Batch upsert when reaching batch_size
            if len(vectors_batch) >= batch_size:
                index.upsert(vectors=vectors_batch, namespace="paper-card")
                vectors_batch = []

    # Upsert any remaining vectors
    if vectors_batch:
        index.upsert(vectors=vectors_batch, namespace="paper-card")

def main_upsert_card():

    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME')

    # Configuration
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    #
    # Load and process files
    #files = load_json_files()
    #data = {}
    #
    #for f in files:
    #    try:
    #        with open(f'./paper_cards/{f}', encoding='utf-8') as f_j:
    #            tmp_j = f_j.read()
    #            card, paper_id = extract_questions_and_filename(f, tmp_j)
    #            data[paper_id] = card 
    #    except Exception as e:
    #        print(f"Error processing {f}: {e}")
    #        continue
    #
    ## Initialize Pinecone and upsert data
    ##index = initialize_pinecone(PINECONE_API_KEY, PINECONE_ENV, INDEX_NAME)
    #upsert_to_pinecone(index, data)
    
    print("Data successfully indexed in Pinecone!")
    
    # Example query
    def query_similar_questions(query: str, top_k: int = 5):
        query_embedding = get_embeddings(query)
        if query_embedding:
            results = index.query(
                namespace="paper-card",
                vector=query_embedding[0],
                top_k=top_k,
                include_metadata=True
            )
            return results
   
    # Example usage of query
    similar_questions = query_similar_questions("his study, focusing on the challenges posed by hallucinations in LLMs and their impact on information retrieval systems.")
    for match in similar_questions['matches']:
        print(f"Score: {match['score']}")
        print(f"Question: {match['metadata']['question']}")
        print(f"Paper: {match['metadata']['paper_id']}\n")


main_upsert_card()
