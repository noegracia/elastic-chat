import click
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

# Load environment variables
load_dotenv("../.env")  # Adjust this path to where your .env file is located

# Required Environment Variables
cloud_id = os.getenv('ELASTIC_CLOUD_ID')
cloud_user = os.getenv('ELASTIC_USERNAME')
cloud_pass = os.getenv('ELASTIC_PASSWORD')

# Connect to Elastic Cloud cluster
def es_connect(cloud_id, user, passwd):
    es = Elasticsearch(cloud_id=cloud_id, http_auth=(user, passwd))
    return es

# Connect to your Elasticsearch cluster outside of the click command to avoid re-connection on every command call
es = es_connect(cloud_id, cloud_user, cloud_pass)

def index_document(es, index_name, chunk, pdf_path, idx):
    """
    Indexes a given text chunk into Elasticsearch.
    """
    document = {
        "title": f"{os.path.basename(pdf_path)} Chunk {idx}",  # The title of the pdf
        "body": chunk.page_content,  # The text content of the chunk
        "url": pdf_path  # The URL or path to the original document
        # Include other fields as necessary
    }
    response = es.index(index=index_name, id=idx, body=document)
    return response

def process_pdf_to_es(es, index_name, pdf_path):
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
        response = index_document(es, index_name, chunk, pdf_path, idx)
        print(f"Indexed chunk {idx}: {response}")

@click.command()
@click.option('--index_name', default='search-elastic-docs', help='The name of the Elasticsearch index.')
@click.option('--pdf_path', default='pdf/cv.pdf', help='The path to the PDF file to be processed.')
def main(index_name, pdf_path):
    process_pdf_to_es(es, index_name, pdf_path)

if __name__ == '__main__':
    main()
