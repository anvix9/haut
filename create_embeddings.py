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

res = "Q1: What is the primary problem addressed by this research paper?\n\nThe primary problem addressed by this research paper is the inefficient management of key-value (KV) cache memory in large language models (LLMs), which limits their serving performance.\n\nQ2: What motivates the development of this solution, and what are the costs associated with LLM serving systems?\n\nThe motivation behind this solution is to reduce the costs associated with running LLMs. According to recent estimates, processing an LLM request can be 10 times more expensive than a traditional keyword query. Existing LLM serving systems struggle due to poor memory management, resulting in wasted memory and reduced throughput.\n\nQ3: What specific challenges does the existing approach face, and how do they impact performance?\n\nExisting LLM serving systems face two main challenges:\n\n1. Internal fragmentation: storing KV cache in contiguous space leads to severe internal fragmentation, wasting memory.\n2. External fragmentation: pre-allocated sizes for each request lead to external fragmentation, further reducing usable memory.\n\nQ4: What is the proposed solution, and how does it address the existing challenges?\n\nThe proposed solution is PagedAttention, an attention algorithm inspired by operating system virtual memory and paging techniques. It divides the KV cache into blocks, allowing for flexible management, reduced internal fragmentation, and elimination of external fragmentation.\n\nQ5: What is the outcome of implementing this solution, and how does it compare to existing systems?\n\nThe proposed vLLM (Virtual LLM) serving engine, built on top of PagedAttention, achieves near-zero waste in KV cache memory. Evaluations show that vLLM improves throughput by 2-4 times compared to state-of-the-art systems without affecting model accuracy.\n\nContribution: The research paper makes significant contributions to the field by:\n\n* Identifying challenges in memory allocation for LLMs and their impact on performance.\n* Proposing PagedAttention, an attention algorithm addressing these challenges.\n* Designing and implementing vLLM, a high-throughput distributed LLM serving engine with efficient memory management.\n* Demonstrating substantial improvements over previous state-of-the-art solutions.",

#embed = get_embeddings("Hello World, I am a scientist.")
#print(len(embed[0]), embed)


