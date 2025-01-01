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
    ## Query interface 

    # Test query
    query = "Can Gemini, a family of highly capable multimodal models, be fine-tuned to achieve human-expert performance in various reasoning tasks?"
    results_questions = utils.two_stage_retrieval(pinecone_service, query) 
    tmp_res = results_questions
    print(tmp_res)
    #results_card = utils.two_stage_retrieval(pinecone_service,tmp_res, namespace='paper-card')

#    print(results_card)

if __name__ == "__main__":
    main()
