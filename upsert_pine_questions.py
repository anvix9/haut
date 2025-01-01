import os
import services
import data_loader
from dotenv import load_dotenv

def main():

    # Load environment variables
    ## Upsert main-research-questions 
    load_dotenv()
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME')

    # Initialize services
    pinecone_service = services.PineconeService(api_key, index_name)
    #Load and process files

    loader = data_loader.DataLoader()

    data = loader.load_analysis_json_file()
    namespace = "main-research-questions"
    pinecone_service.upsert_documents(data, namespace)
    
if __name__ == "__main__":
    main()