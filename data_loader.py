from pathlib import Path
from typing import Dict
import json

class DataLoader:
    @staticmethod
    def load_markdown_files(directory: str = './paper_cards/', papers_json_path: str = './paper_metadata/arxiv_data.json') -> Dict[str, Dict]:
        """
        Load markdown files and corresponding paper metadata from JSON
        
        Args:
            directory: Directory containing markdown files
            papers_json_path: Path to JSON file containing paper metadata
            
        Returns:
            Dictionary with paper_id as key and dict containing content and metadata as value
        """
        # Load paper metadata from JSON
        try:
            with open(papers_json_path, 'r', encoding='utf-8') as f:
                papers_metadata = {paper['id']: paper for paper in json.load(f)}
        except Exception as e:
            print(f"Error reading metadata JSON: {e}")
            papers_metadata = {}
        
        # Load markdown files and combine with metadata
        files_content = {}
        
        for file_path in Path(directory).glob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    paper_id = file_path.name.replace('_card.md', '')
                    
                    # Create document with content and metadata
                    document = {
                        'content': content,
                        'metadata': {
                            'paper_id': paper_id,
                            'title': papers_metadata.get(paper_id, {}).get('title', ''),
                            'authors': papers_metadata.get(paper_id, {}).get('authors', []),
                            'submission_date': papers_metadata.get(paper_id, {}).get('submission_date', ''),
                            'link': papers_metadata.get(paper_id, {}).get('link', '')
                        }
                    }
                    
                    files_content[paper_id] = document
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return files_content


