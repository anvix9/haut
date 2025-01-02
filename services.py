import requests
import numpy as np
from typing import List, Optional, Dict
from pinecone.grpc import PineconeGRPC
from flashrank import Ranker, RerankRequest
from tqdm import tqdm

class EmbeddingService:
    def __init__(self, model_name: str = "saish_15/tethysai_research", url: str = "http://127.0.0.1:11434/api/embed"):
        self.model_name = model_name
        self.url = url

    def get_embeddings(self, content: str) -> Optional[List[float]]:
        """
        Get embeddings from Ollama with proper normalization
        
        Args:
            content: Text content to embed
            
        Returns:
            Normalized embedding vector or None if failed
        """
        payload = {
            "model": self.model_name,
            "input": content  # Remove the "Content: " prefix to maintain consistency
        }
        
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            embeddings = response.json().get('embeddings')
            
            if not embeddings:
                print("No embeddings returned from API")
                return None
                
            # Normalize the embedding vector
            embedding_array = np.array(embeddings[0])
            normalized_embedding = embedding_array / np.linalg.norm(embedding_array)
            
            return normalized_embedding.tolist()
            
        except Exception as e:
            print(f"Error extracting embedding: {str(e)}")
            return None

class PineconeService:
    def __init__(self, api_key: str, index_name: str):
        self.pc = PineconeGRPC(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.embedding_service = EmbeddingService()
    
    def _create_vector(self, id: str, embedding: List[float], metadata: Dict) -> Dict:
        """Create a properly formatted vector for Pinecone"""
        return {
            'id': id,
            'values': embedding,
            'metadata': metadata
        }
    
    def upsert_documents(self, data: Dict[str, Dict], namespace: str = "main-research-questions", batch_size: int = 100) -> None:
        """Upsert documents with enhanced metadata to Pinecone"""
        vectors_batch = []
        processed = 0
        
        for paper_id, document in tqdm(data.items(), desc="Processing documents"):
            try:
                if namespace == "paper-card":
                    content = document.get('content', '')
                    embedding = self.embedding_service.get_embeddings(content)
                    
                    if embedding:
                        vector = self._create_vector(
                            id=paper_id,
                            embedding=embedding,
                            metadata={
                                'paper_id': paper_id,
                                'text': content,
                                'title': document['metadata']['title'],
                                'authors': document['metadata']['authors'],
                                'submission_date': document['metadata']['submission_date'],
                                'link': document['metadata']['link']
                            }
                        )
                        vectors_batch.append(vector)
                else:
                    questions = document.get('questions', '')
                    embedding = self.embedding_service.get_embeddings(questions)
                    
                    if embedding:
                        vector = self._create_vector(
                            id=paper_id,
                            embedding=embedding,
                            metadata={
                                'paper_id': paper_id,
                                'text': questions
                            }
                        )
                        vectors_batch.append(vector)
                
                processed += 1
                if len(vectors_batch) >= batch_size:
                    self.index.upsert(vectors=vectors_batch, namespace=namespace)
                    print(f"Upserted batch of {len(vectors_batch)} vectors")
                    vectors_batch = []
                    
            except Exception as e:
                print(f"Error processing document {paper_id}: {e}")
        
        if vectors_batch:
            self.index.upsert(vectors=vectors_batch, namespace=namespace)
            print(f"Upserted final batch of {len(vectors_batch)} vectors")
            
        print(f"Successfully processed {processed} documents")

    def query_similar(self, query: str, namespace: str, top_k: int = 20) -> Optional[Dict]:
        """
        Query similar documents with normalized embeddings
        
        Args:
            query: Query string
            namespace: Pinecone namespace
            top_k: Number of results to return
        """
        try:
            if(isinstance(query, str)):
                query_embedding = self.embedding_service.get_embeddings(query)
            else:
                query_embedding = query
                
            if not query_embedding:
                print("Failed to generate query embedding")
                return None
            
            print(f"Querying namespace: {namespace}")
            print(f"Query: '{query[:100]}...'")  # Print first 100 chars of query
            
            results = self.index.query(
                namespace=namespace,
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Print some debug info
            if results and results.get('matches'):
                print(f"Found {len(results['matches'])} matches")
                print("Top 3 scores:", [match.score for match in results['matches'][:3]])
            else:
                print("No matches found")
                
            return results
            
        except Exception as e:
            print(f"Error during query: {e}")
            return None

    def rerank_results(self, query: str, documents: List[str], top_n: int = 10) -> Dict:
        """Rerank results using BGE reranker"""
        ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="~/cache")
        rerankrequest = RerankRequest(query=query, passages=documents)
        results = ranker.rerank(rerankrequest) 
        return results
        #try:
        #    return self.pc.inference.rerank(
        #        model="bge-reranker-v2-m3",
        #        query=query,
        #        documents=documents,
        #        top_n=top_n,
        #        return_documents=True,
        #        parameters={"truncate": "END"}
        #    )
        #except Exception as e:
        #    print(f"Error during reranking: {e}")
        #    return None
