from pathlib import Path 
import json 
import re 
import services 
import data_loader

def load_json_files(directory='./paper_analysis/'):
    """
    Load all JSON files from the specified directory.
    Args:
        directory (str): Path to the directory containing JSON files. Defaults to current directory.
    Returns:
        dict: Dictionary with filenames as keys and JSON content as values
    """
    json_files = {}
    
    # Get all JSON files in the directory
    for file_path in Path(directory).glob('*.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Load JSON content
                json_content = json.load(file)
                # Use filename as key
                json_files[file_path.name] = json_content
        except json.JSONDecodeError as e:
            print(f"Error decoding {file_path}: {e}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return json_files

def extract_questions_and_filename(source, text):
    # Extract questions
    pattern = r'Q\d+: (.+?)(?=\n|$)'
    questions = re.findall(pattern, text)
    
    # Extract filename without '_analysis.json'
    filename = source.replace('_analysis.json', '')
    
    return questions, filename

# Two-stage retrieval
def two_stage_retrieval(pinecone_service, query: str, namespace: str = "main-research-questions", first_stage_k: int = 20, final_k: int = 10):
    # First stage: Semantic search
    initial_results = pinecone_service.query_similar(query, namespace, first_stage_k)
    if not initial_results:
        return None
        
    # Extract documents for reranking
    documents = [match.metadata.get('question', '') for match in initial_results['matches']]
    
    # Second stage: Reranking
    reranked_results = pinecone_service.rerank_results(query, documents, final_k)
    
    return reranked_results

# Upserting
def upsert_documents(pinecone_service):
    data_loader_ = data_loader.DataLoader()
    documents = data_loader_.load_markdown_files()
    pinecone_service.upsert_documents(documents)


