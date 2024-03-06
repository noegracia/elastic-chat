import click
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from dotenv import load_dotenv
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import json

# Load environment variables
load_dotenv("../.env")  # Adjust this path to where your .env file is located

# Required Environment Variables
cloud_id = os.getenv('ELASTIC_CLOUD_ID')
cloud_user = os.getenv('ELASTIC_USERNAME')
cloud_pass = os.getenv('ELASTIC_PASSWORD')

# Function to check if pipeline exists and create it if not
def create_pipeline_with_file(es_client, pipeline_id, pipeline_file):
        
    # Load the pipeline definition from the file
    with open(pipeline_file, 'r') as file:
        pipeline_body = json.load(file)

    # If the pipeline is not found, create it
    response = es_client.ingest.put_pipeline(id=pipeline_id, body=pipeline_body)
    if response.get('acknowledged', False):
        print(f"Pipeline '{pipeline_id}' created successfully.")
    else:
        print(f"Failed to create pipeline '{pipeline_id}'.")

# Connect to Elastic Cloud cluster
def es_connect(cloud_id, user, passwd):
    es = Elasticsearch(cloud_id=cloud_id, http_auth=(user, passwd))
    return es

def index_document(es, index_name, chunk, pdf_path, idx, pipeline_name):
    """
    Indexes a given text chunk into Elasticsearch.
    """
    document = {
        "title": f"{os.path.basename(pdf_path)} Chunk {idx}",  # The title of the pdf
        "body_content": chunk.page_content,  # The text content of the chunk
        "url": pdf_path  # The URL or path to the original document
        # Include other fields as necessary
    }
    response = es.index(index=index_name, id=idx, body=document, pipeline=pipeline_name)
    return response

def process_pdf_to_es(es, index_name, pipeline_name, pdf_path):
    """
    Processes a PDF file, splits it into chunks, and indexes those chunks into Elasticsearch.
    """
    # Load the PDF
    doc_loader = PyMuPDFLoader(pdf_path)
    
    # Split the document into chunks
    chunk_size = 500  # Adjust based on your needs
    chunk_overlap = 50  # Adjust based on your needs
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunked_documents = doc_loader.load_and_split(text_splitter)
    
    # Index each chunk into Elasticsearch
    for idx, chunk in enumerate(chunked_documents):
        response = index_document(es, index_name, chunk, pdf_path, idx, pipeline_name)
        print(f"Indexed chunk {idx}: {response}")

@click.command()
@click.option('--index_name', default='search-elastic-docs', help='The name of the Elasticsearch index.')
@click.option('--pipeline_name', default=None, help='The name of the Ingest Attachment Processor pipeline to use.')
@click.option('--pipeline_file', default=None, help='The path to the pipeline definition file.')
@click.option('--pdf_path', default='pdf/cv.pdf', help='The path to the PDF file to be processed.')
def main(index_name, pipeline_name, pipeline_file, pdf_path):

    # Connect to your Elasticsearch cluster outside of the click command to avoid re-connection on every command call
    es = es_connect(cloud_id, cloud_user, cloud_pass)

    if pipeline_name is None:
        pipeline_name = 'ml-inference-body-content'
        print('Using the default pipeline name `ml-inference-body-content`.')

    # Check if the pipeline already exists
    print(f"Checking if pipeline '{pipeline_name}' exists...")
    try:
        # Try to get the pipeline to see if it already exists
        es.ingest.get_pipeline(id=pipeline_name)
        print(f"Pipeline '{pipeline_name}' exists. Proceeding to process the PDF.")
    except NotFoundError:
        # Create the pipeline if it does not exist
        if pipeline_file is not None:
            print(f"Creating pipeline '{pipeline_name}' from file '{pipeline_file}'...")
            create_pipeline_with_file(es, pipeline_name, pipeline_file)
        else:
            print("Pipeline does not exist and no pipeline file provided. Exiting.")
            return

    # Process the PDF and index it into Elasticsearch
    process_pdf_to_es(es, index_name, pipeline_name, pdf_path)


if __name__ == '__main__':
    main()
