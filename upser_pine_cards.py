# embedding_service.py
import requests
from typing import List, Optional

class EmbeddingService:
    def __init__(self, model_name: str = "saish_15/tethysai_research", url: str = "http://127.0.0.1:11434/api/embed"):
        self.model_name = model_name
        self.url = url

    def get_embeddings(self, content: str) -> Optional[List[float]]:
        """Get embeddings from Ollama"""
        payload = {
            "model": self.model_name,
            "input": f"Content: {content}"
        }
        
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            return response.json()['embeddings']
        except Exception as e:
            print(f"Error extracting embedding: {str(e)}")
            return None

# pinecone_service.py
from pinecone.grpc import PineconeGRPC
from typing import Dict, List, Optional
from tqdm import tqdm

class PineconeService:
    def __init__(self, api_key: str, index_name: str):
        self.pc = PineconeGRPC(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.embedding_service = EmbeddingService()

    def upsert_documents(self, data: Dict[str, str], namespace: str = "main-research-questions", batch_size: int = 100) -> None:
        """Upsert documents to Pinecone"""
        vectors_batch = []
        
        for paper_id, card in tqdm(data.items(), desc="Processing documents"):
            embedding = self.embedding_service.get_embeddings(card)
            if embedding:
                vector = {
                    'id': f"{paper_id}",
                    'values': embedding[0],
                    'metadata': {
                        'paper_id': paper_id,
                        'question': card,
                    }
                }
                vectors_batch.append(vector)
                
                if len(vectors_batch) >= batch_size:
                    self.index.upsert(vectors=vectors_batch, namespace=namespace)
                    vectors_batch = []

        if vectors_batch:
            self.index.upsert(vectors=vectors_batch, namespace=namespace)

    def query_similar(self, query: str, namespace: str, top_k: int = 20) -> dict:
        """Query similar documents"""
        query_embedding = self.embedding_service.get_embeddings(query)
        if query_embedding:
            return self.index.query(
                namespace=namespace,
                vector=query_embedding[0],
                top_k=top_k,
                include_metadata=True
            )
        return None

    def rerank_results(self, query: str, documents: List[str], top_n: int = 10) -> dict:
        """Rerank results using BGE reranker"""
        return self.pc.inference.rerank(
            model="bge-reranker-v2-m3",
            query=query,
            documents=documents,
            top_n=top_n,
            return_documents=True,
            parameters={"truncate": "END"}
        )

# data_loader.py
from pathlib import Path

class DataLoader:
    @staticmethod
    def load_markdown_files(directory: str = './paper_cards/') -> Dict[str, str]:
        """Load all markdown files from directory"""
        files_content = {}
        
        for file_path in Path(directory).glob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    paper_id = file_path.name.replace('_card.md', '')
                    files_content[paper_id] = content
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return files_content

# main.py
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME')

    # Initialize services
    pinecone_service = PineconeService(api_key, index_name)
    
    # Example of two-stage retrieval
    def two_stage_retrieval(query: str, namespace: str = "main-research-questions", first_stage_k: int = 20, final_k: int = 10):
        # First stage: Semantic search
        initial_results = pinecone_service.query_similar(query, namespace, first_stage_k)
        if not initial_results:
            return None
            
        # Extract documents for reranking
        documents = [match.metadata.get('question', '') for match in initial_results['matches']]
        
        # Second stage: Reranking
        reranked_results = pinecone_service.rerank_results(query, documents, final_k)
        
        return reranked_results

    # Example usage for upserting
    def upsert_documents():
        data_loader = DataLoader()
        documents = data_loader.load_markdown_files()
        pinecone_service.upsert_documents(documents)

    # Example query
    query = "Can Gemini, a family of highly capable multimodal models, be fine-tuned to achieve human-expert performance in various reasoning tasks?"
    results_questions = two_stage_retrieval(query)
    tmp_res = results_questions.data[0]["document"]["text"]
    results_card = two_stage_retrieval(tmp_res, namespace='paper-card')

    print(results_card)

if __name__ == "__main__":
    main()
