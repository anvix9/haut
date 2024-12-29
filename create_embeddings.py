import requests
import re 
import json 

def get_embeddings(content):
    """Get embeddings from tethysai_research"""
    _url = "http://127.0.0.1:11434/api/embed"

    print("Extracting embeddings...")
    
    _custom_prompt = (
        f"Content: {content}"
    )
    
    _payload = {
        "model": "saish_15/tethysai_research",
        "input": _custom_prompt
    }
    
    try:
        response = requests.post(_url, data=json.dumps(_payload))
        response.raise_for_status()
        response_data = response.json()
        
        # Clean the response to ensure it's a valid Python list
        emb = response_data['embeddings']
        return emb 
    except Exception as e:
        print(f"Error extracting embedding: {str(e)}")
        return ["Embedding extraction failed"]


## Index haut_main_questions


embed = get_embeddings("Hello World, I am a scientist.")
print(len(embed[0]), embed)

