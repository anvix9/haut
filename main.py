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
    
    # Convert PDF ->  [markdown]
    
    # Parse and select sections from Markdown 

    # Save Metadata 

    # Generate main reaearch questions answered 

    # Generate paper cards 

    # Generate gap or future questions 

    # Upserting them
    #utils.upsert_documents(pinecone_service)

    # Query interface 

    # Test query
    query = "Can Gemini, a family of highly capable multimodal models, be fine-tuned to achieve human-expert performance in various reasoning tasks?"
    results_questions = utils.two_stage_retrieval(pinecone_service, query)
    tmp_res = results_questions.data[0]["document"]["text"]
    results_card = utils.two_stage_retrieval(pinecone_service,tmp_res, namespace='paper-card')

    print(results_card)

if __name__ == "__main__":
    main()
