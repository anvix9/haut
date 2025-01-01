import requests
from typing import List, Optional
from pinecone.grpc import PineconeGRPC
from typing import Dict, List, Optional
from tqdm import tqdm

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

class PineconeService:
    def __init__(self, api_key: str, index_name: str):
        self.pc = PineconeGRPC(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.embedding_service = EmbeddingService()
    
    def upsert_documents(self, data: Dict[str, Dict], namespace: str = "main-research-questions", batch_size: int = 100) -> None:
        """
        Upsert documents with enhanced metadata to Pinecone
        
        Args:
            data: Dictionary containing document content and metadata
            namespace: Pinecone namespace
            batch_size: Number of vectors to upsert in each batch
        """
        vectors_batch = []
        
        for paper_id, document in tqdm(data.items(), desc="Processing documents"):

            if(namespace == "paper-card"):
                embedding = self.embedding_service.get_embeddings(document['content'])
                if embedding:
                    vector = {
                        'id': f"{paper_id}",
                        'values': embedding[0],
                        'metadata': {
                            'paper_id': paper_id,
                            'content': document['content'],
                            'title': document['metadata']['title'],
                            'authors': document['metadata']['authors'],
                            'submission_date': document['metadata']['submission_date'],
                            'link': document['metadata']['link']
                        }
                    }
                    vectors_batch.append(vector)
                    
                    if len(vectors_batch) >= batch_size:
                        self.index.upsert(vectors=vectors_batch, namespace=namespace)
                        vectors_batch = []
            

            else:
                embedding = self.embedding_service.get_embeddings(document['questions'])
                if embedding:
                    vector = {
                        'id': f"{paper_id}",
                        'values': embedding[0],
                        'metadata': {
                            'questions': document['questions'],
                            'paper_id': paper_id,
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
