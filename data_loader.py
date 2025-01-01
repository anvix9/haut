from pathlib import Path
from typing import Dict
import json
import utils

class DataLoader:
    @staticmethod
    def load_analysis_json_file(directory: str = './paper_analysis/', 
                          papers_json_path: str = './paper_metadata/metadata_2024_12_31_143026.json') -> Dict[str, Dict]:
        """
        Load json files containing paper analysis and corresponding paper metadata
        
        Args:
            directory: Directory containing json analysis files
            papers_json_path: Path to JSON file containing paper metadata
                
        Returns:
            Dictionary with paper_id as key and dict containing analysis content, questions and metadata as value
        """
        # Load paper metadata from JSON
        try:
            with open(papers_json_path, 'r', encoding='utf-8') as f:
                papers_metadata = json.load(f)
        except Exception as e:
            print(f"Error reading metadata JSON: {e}")
            papers_metadata = {}
        
        # Load and process analysis files
        files_content = {}
        
        for file_path in Path(directory).glob('*_analysis.json'):
            try:
                # Read and parse JSON file
                with open(file_path, 'r', encoding='utf-8') as file:
                    analysis_data = json.load(file)
                    
                # Extract paper ID from filename
                filename = file_path.stem  # Gets filename without extension
                tag, paper_id = filename.replace('_analysis', '').split("_")
                
                # Extract research questions
                research_content = analysis_data.get("research", "")
                questions, _ = utils.extract_questions_and_filename(file_path.name, research_content)
                
                # Create document with content and metadata
                document = {
                    'questions': questions,
                    'metadata': {
                        'paper_id': paper_id,
                    }
                }
                    
                files_content[paper_id] = document
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        return files_content   
    
    @staticmethod
    def load_card_markdown(directory: str = './card_papers/', papers_json_path: str = './paper_metadata/metadata_2024_12_31_143026.json') -> Dict[str, Dict]:
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
                papers_metadata = json.load(f)
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
                    tag, paper_id = paper_id.split("_")
                    # Create document with content and metadata
                    document = {
                        'content': content,
                        'metadata': {
                            'paper_id': paper_id,
                            'title': next((paper['title'] for paper in papers_metadata if paper['id'] == paper_id), "Unknown Title"),
                            'authors': next((paper['authors'] for paper in papers_metadata if paper['id'] == paper_id), "Unknown authors"),
                            'submission_date': next((paper['submission_date'] for paper in papers_metadata if paper['id'] == paper_id), "Unknown Date"),
                            'link': next((paper['link'] for paper in papers_metadata if paper['id'] == paper_id), "Unknown Link")                        
                            }
                    }
                    
                    files_content[paper_id] = document
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return files_content



