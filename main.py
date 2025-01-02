import os
from dotenv import load_dotenv
import services 
import utils 

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = os.getenv('PINECONE_INDEX_NAME')

    # Initialize services
    pinecone_service = services.PineconeService(api_key, index_name)
    
    # Backend processes
    ## Convert PDF ->  [markdown]
    ## pdf_md_converter.py

    ## Parse and select sections from Markdown 
    ## paper_compresser.py    

    ## Save Metadata 
    ## get_metadata.py 

    ## Generate main reaearch questions answered 
    ## question_generation.py

    ## Generate paper cards 
    ## generate_card.py 

    ## Generate gap or future questions 
    ## question_future.py 

    ## Upserting them
#    services.upsert_documents(pinecone_service)

    # FrontEnd
    # Main query interface
    query = "What is Gemini?"

    try:
        results = utils.fetch_and_query(
            pinecone_service, 
            query=query, 
            primary_namespace='main-research-questions', 
            secondary_namespace='paper-card'
        )
        for card in results:
            print(f"{card['link']} - score {card['score']}")
    except ValueError as e:
        print(f"Error: {e}")



if __name__ == "__main__":
    main()
